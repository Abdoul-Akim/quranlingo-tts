#!/bin/zsh
# Runs the pipeline for some languages, one heavy model at a time. Resumable: finished clips are
# skipped, so after an interruption run the same command again. A failing stage is logged and
# the run carries on. Progress goes to outputs/logs/run.log, each stage's output to its own log.
#
# Run from the TTS folder:
#   caffeinate -i zsh tools/run.sh <steps> <languages...>
#   caffeinate -i zsh tools/run.sh pick,lines,similarity,rounds fr de
#   caffeinate -i zsh tools/run.sh all all
#   DRY=1 zsh tools/run.sh all fr        prints the commands without running anything
#
# Steps (comma separated, always run in this order; "all" is every step except parler and variations):
#   design      base voice takes with VoxCPM2 (tools/base_voices.py says which)
#   check       word check and pitch of the base takes
#   pick        each character's voice into voices/<lang>/ (owner's shortlist, else the ranking)
#   lines       test lines on both engines (no Chatterbox for Urdu), with their word checks
#   experiment  the English voices speaking this language (not for English)
#   similarity  voice consistency of every test line folder
#   rounds      website rounds; the old rounds and keys move to outputs/archive first
#   variations  every character in every emotion
#   parler      Indic Parler-TTS base voices (ur, hi only; needs the terms accepted on Hugging Face)
#   report      outputs/report.md
cd "${0:A:h}/.."
TTS="$PWD"
LOG="$TTS/outputs/logs"
mkdir -p "$LOG"
RUN="$LOG/run.log"
ALL_LANGUAGES=(en fr ar de tr hi ur)

if (( $# < 2 )); then
  sed -n '2,22p' "$0" | cut -c3-
  exit 1
fi
STEPS=",$1,"
[[ $1 == all ]] && STEPS=",design,check,pick,lines,experiment,similarity,rounds,report,"
shift
LANGS=("$@")
[[ $1 == all ]] && LANGS=($ALL_LANGUAGES)
wants() { [[ $STEPS == *",$1,"* ]] }

stage() {  # stage <name> <command...>
  local name=$1; shift
  if [[ -n $DRY ]]; then print "$name: $*"; return; fi
  print "$(date '+%H:%M') start $name" >> "$RUN"
  if "$@" >> "$LOG/$name.log" 2>&1; then
    print "$(date '+%H:%M') done  $name" >> "$RUN"
  else
    print "$(date '+%H:%M') FAILED $name (see $name.log)" >> "$RUN"
  fi
}
vox()     { (cd "$TTS/engines/voxcpm2" && uv run python "$@") }
chatter() { (cd "$TTS/engines/chatterbox" && uv run python "$@") }
parler()  { (cd "$TTS/engines/parler" && uv run python "$@") }
tool()    { uv run --project "$TTS/analysis" python -W ignore "$@" }
archive_rounds() {  # make_round never overwrites, so the old rounds and keys move aside
  local dest="$TTS/outputs/archive/rounds_replaced_$(date '+%Y-%m-%d_%H%M')"
  for k in base lines experiment; do
    [[ -d listening_site/rounds/${k}_$1 ]] && mkdir -p "$dest/rounds" && mv listening_site/rounds/${k}_$1 "$dest/rounds/"
    [[ -f keys/${k}_$1.json ]] && mkdir -p "$dest/keys" && mv keys/${k}_$1.json "$dest/keys/"
  done
  return 0
}

[[ -z $DRY ]] && print "$(date '+%H:%M') RUN $STEPS ${LANGS[*]}" >> "$RUN"
for l in $LANGS; do
  engines=(voxcpm2)
  [[ $l != ur ]] && engines+=(chatterbox)  # Chatterbox has no Urdu
  base="outputs/base_voices/$l"

  wants design && stage "design_$l" vox design_base_voices.py $l
  wants check  && stage "check_base_$l" tool tools/check_clips.py $l passage $base
  wants pick   && stage "pick_$l" tool tools/rank_takes.py $base voices/$l
  if wants lines; then
    stage "lines_vox_$l" vox generate.py $l
    [[ $l != ur ]] && stage "lines_chatter_$l" chatter generate.py $l
    for e in $engines; do stage "check_lines_${l}_$e" tool tools/check_clips.py $l lines outputs/step1_$l/$e; done
  fi
  if wants experiment && [[ $l != en ]]; then
    stage "experiment_vox_$l" vox generate.py $l --voices-from en
    [[ $l != ur ]] && stage "experiment_chatter_$l" chatter generate.py $l --voices-from en
    for e in $engines; do stage "check_lines_${l}_${e}_voice_en" tool tools/check_clips.py $l lines outputs/step1_$l/${e}_voice_en; done
  fi
  if wants similarity; then
    for d in outputs/step1_$l/*(/N); do stage "similarity_${l}_${d:t}" chatter speaker_similarity.py $l "$TTS/$d"; done
  fi
  if wants rounds; then
    [[ -n $DRY ]] && print "archive old rounds and keys of $l" || archive_rounds $l
    stage "round_base_$l" python3 tools/make_round.py base base_$l $l
    [[ $l != ur ]] && stage "round_lines_$l" python3 tools/make_round.py engines lines_$l $l chatterbox voxcpm2
    [[ $l != en ]] && stage "round_experiment_$l" python3 tools/make_round.py experiment experiment_$l $l voxcpm2 en
  fi
  if wants variations; then
    stage "variations_vox_$l" vox generate.py $l --set variations
    [[ $l != ur ]] && stage "variations_chatter_$l" chatter generate.py $l --set variations
  fi
  wants parler && [[ $l == (ur|hi) ]] && stage "parler_$l" parler design_base_voices.py $l
  [[ -z $DRY ]] && print "$(date '+%H:%M') LANGUAGE READY $l" >> "$RUN"
done

wants report && stage report python3 tools/summarise.py
[[ -z $DRY ]] && print "$(date '+%H:%M') ALL DONE" >> "$RUN"
exit 0
