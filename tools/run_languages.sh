#!/bin/zsh
# Redo the other languages with the wordings the owner chose in English (2026-11-08):
# base voices, automatic picks, test lines on both engines, the English voice experiment,
# checks and website rounds. One language at a time, French and Arabic first (the owner
# can judge those). Resumable; a failing stage is logged and the run carries on.
#
# Run from the TTS folder:  caffeinate -i zsh tools/run_languages.sh
cd "${0:A:h}/.."
TTS="$PWD"
LOG="$TTS/outputs/logs"
mkdir -p "$LOG"
RUN="$LOG/languages.log"

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

for l in fr ar de tr hi ur; do
  stage "v2_base_$l"       vox design_base_voices.py $l
  stage "v2_check_base_$l" tool tools/check_clips.py $l passage outputs/base_voices/$l
  stage "v2_pick_$l"       tool tools/rank_takes.py outputs/base_voices/$l voices/$l
  stage "v2_lines_vox_$l"        vox generate.py $l
  stage "v2_experiment_vox_$l"   vox generate.py $l --voices-from en
  if [[ $l != ur ]]; then  # Chatterbox has no Urdu
    stage "v2_lines_chatter_$l"      chatter generate.py $l
    stage "v2_experiment_chatter_$l" chatter generate.py $l --voices-from en
  fi
  for d in outputs/step1_$l/*(/N); do
    stage "v2_check_lines_${l}_${d:t}" tool tools/check_clips.py $l lines $d
    stage "v2_similarity_${l}_${d:t}"  chatter speaker_similarity.py $l "$TTS/$d"
  done
  stage "v2_round_base_$l" python3 tools/make_round.py base base_$l $l
  [[ $l != ur ]] && stage "v2_round_lines_$l" python3 tools/make_round.py engines lines_$l $l chatterbox voxcpm2
  stage "v2_round_experiment_$l" python3 tools/make_round.py experiment experiment_$l $l voxcpm2 en
  print "$(date '+%H:%M') LANGUAGE READY $l" >> "$RUN"
done

stage v2_report python3 tools/summarise.py
print "$(date '+%H:%M') ALL DONE" >> "$RUN"
