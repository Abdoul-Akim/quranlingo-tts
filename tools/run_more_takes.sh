#!/bin/zsh
# After tools/run_picks.sh: redo French with Fatima's new voice, and give Turkish, Hindi and
# Urdu more base voice takes (seeds 4 to 6), then picks, lines, checks and rounds again.
# Waits for run_picks.sh to finish first (one heavy model at a time). Resumable.
#
# Run from the TTS folder:  caffeinate -i zsh tools/run_more_takes.sh
cd "${0:A:h}/.."
TTS="$PWD"
LOG="$TTS/outputs/logs"
RUN="$LOG/more_takes.log"
ARCHIVE="$TTS/outputs/archive/rounds_replaced_$(date '+%Y-%m-%d_%H%M')"

until grep -q "ALL DONE" "$LOG/picks.log" 2>/dev/null; do sleep 60; done

stage() {  # stage <name> <command...>
  local name=$1; shift
  print "$(date '+%H:%M') start $name" >> "$RUN"
  if "$@" >> "$LOG/$name.log" 2>&1; then
    print "$(date '+%H:%M') done  $name" >> "$RUN"
  else
    print "$(date '+%H:%M') FAILED $name (see $name.log)" >> "$RUN"
  fi
}
vox()     { (cd "$TTS/engines/voxcpm2" && uv run python "$@") }
chatter() { (cd "$TTS/engines/chatterbox" && uv run python "$@") }
tool()    { uv run --project "$TTS/analysis" python -W ignore "$@" }
archive_rounds() {  # make_round never overwrites, so the old rounds and keys move aside
  mkdir -p "$ARCHIVE/rounds" "$ARCHIVE/keys"
  for k in base lines experiment; do
    [[ -d listening_site/rounds/${k}_$1 ]] && mv listening_site/rounds/${k}_$1 "$ARCHIVE/rounds/"
    [[ -f keys/${k}_$1.json ]] && mv keys/${k}_$1.json "$ARCHIVE/keys/"
  done
}

for l in fr tr hi ur; do
  if [[ $l != fr ]]; then
    stage "v4_base_$l"       vox design_base_voices.py $l
    stage "v4_check_base_$l" tool tools/check_clips.py $l passage outputs/base_voices/$l
  fi
  stage "v4_pick_$l"      tool tools/rank_takes.py outputs/base_voices/$l voices/$l
  stage "v4_lines_vox_$l" vox generate.py $l
  engines=(voxcpm2)
  if [[ $l != ur ]]; then  # Chatterbox has no Urdu
    stage "v4_lines_chatter_$l" chatter generate.py $l
    engines+=(chatterbox)
  fi
  for e in $engines; do
    stage "v4_check_lines_${l}_$e" tool tools/check_clips.py $l lines outputs/step1_$l/$e
    stage "v4_similarity_${l}_$e"  chatter speaker_similarity.py $l "$TTS/outputs/step1_$l/$e"
  done
  archive_rounds $l
  stage "v4_round_base_$l" python3 tools/make_round.py base base_$l $l
  [[ $l != ur ]] && stage "v4_round_lines_$l" python3 tools/make_round.py engines lines_$l $l chatterbox voxcpm2
  stage "v4_round_experiment_$l" python3 tools/make_round.py experiment experiment_$l $l voxcpm2 en
  print "$(date '+%H:%M') LANGUAGE READY $l" >> "$RUN"
done

stage v4_report python3 tools/summarise.py
print "$(date '+%H:%M') ALL DONE" >> "$RUN"
