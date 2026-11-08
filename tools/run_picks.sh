#!/bin/zsh
# Apply the owner's picks (2026-11-08) in the other languages: Ali takes the English voice,
# Fatima, Omar and Zahra the owner's choice (fr, ar) or the pitch-filtered automatic pick.
# Only lines whose voice changed are redone (line_jobs.is_done). Then checks and rounds.
# Old rounds and keys must be archived first (make_round never overwrites).
#
# Run from the TTS folder:  caffeinate -i zsh tools/run_picks.sh
cd "${0:A:h}/.."
TTS="$PWD"
LOG="$TTS/outputs/logs"
mkdir -p "$LOG"
RUN="$LOG/picks.log"

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
  stage "v3_pick_$l"      tool tools/rank_takes.py outputs/base_voices/$l voices/$l
  stage "v3_lines_vox_$l" vox generate.py $l
  engines=(voxcpm2)
  if [[ $l != ur ]]; then  # Chatterbox has no Urdu
    stage "v3_lines_chatter_$l" chatter generate.py $l
    engines+=(chatterbox)
  fi
  for e in $engines; do
    stage "v3_check_lines_${l}_$e" tool tools/check_clips.py $l lines outputs/step1_$l/$e
    stage "v3_similarity_${l}_$e"  chatter speaker_similarity.py $l "$TTS/outputs/step1_$l/$e"
  done
  stage "v3_round_base_$l" python3 tools/make_round.py base base_$l $l
  [[ $l != ur ]] && stage "v3_round_lines_$l" python3 tools/make_round.py engines lines_$l $l chatterbox voxcpm2
  stage "v3_round_experiment_$l" python3 tools/make_round.py experiment experiment_$l $l voxcpm2 en
  print "$(date '+%H:%M') LANGUAGE READY $l" >> "$RUN"
done

stage v3_report python3 tools/summarise.py
print "$(date '+%H:%M') ALL DONE" >> "$RUN"
