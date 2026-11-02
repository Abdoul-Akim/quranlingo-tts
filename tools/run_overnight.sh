#!/bin/zsh
# The whole overnight run, one heavy job at a time, English first.
# Every stage is resumable, so after an interruption just run this again.
# A failing stage is logged and the run carries on with the next one.
#
# Run from the TTS folder:  caffeinate -i zsh tools/run_overnight.sh
cd "${0:A:h}/.."
TTS="$PWD"
LOG="$TTS/outputs/logs"
mkdir -p "$LOG"
OTHER=(fr de tr ar hi)          # supported by both engines
ALL=(en fr de tr ar hi ur)      # ur: VoxCPM2 only, untested experiment

stage() {  # stage <name> <command...>
  local name=$1; shift
  print "$(date '+%H:%M') start $name" >> "$LOG/overnight.log"
  if "$@" >> "$LOG/$name.log" 2>&1; then
    print "$(date '+%H:%M') done  $name" >> "$LOG/overnight.log"
  else
    print "$(date '+%H:%M') FAILED $name (see $name.log)" >> "$LOG/overnight.log"
  fi
}
vox()     { (cd "$TTS/engines/voxcpm2" && uv run python "$@") }
chatter() { (cd "$TTS/engines/chatterbox" && uv run python "$@") }
tool()    { uv run --project "$TTS/analysis" python -W ignore "$@" }

voices_ready() {  # voices_ready <lang>: base voices designed, shifted, checked, picked
  stage "base_$1"   vox design_base_voices.py "$1"
  stage "shift_$1"  tool tools/age_shift.py --plan "outputs/base_voices/$1"
  stage "check_base_$1" tool tools/check_clips.py "$1" passage "outputs/base_voices/$1"
  stage "pick_$1"   tool tools/rank_takes.py "outputs/base_voices/$1" "voices/$1"
}

# 1. English all the way through.
voices_ready en
stage lines_vox_en     vox generate.py en
stage lines_chatter_en chatter generate.py en
stage check_lines_en_vox     tool tools/check_clips.py en lines outputs/step1_en/voxcpm2
stage check_lines_en_chatter tool tools/check_clips.py en lines outputs/step1_en/chatterbox

# 2. Native base voices for the other languages (Urdu last: unsupported by both engines).
for l in $OTHER ur; do voices_ready $l; done

# 3. Native test lines on both engines.
for l in $OTHER; do stage "lines_vox_$l" vox generate.py $l; done
stage lines_vox_ur vox generate.py ur
for l in $OTHER; do stage "lines_chatter_$l" chatter generate.py $l; done

# 4. Side experiment: the English voices speaking the other languages.
stage experiment_vox     vox generate.py $OTHER ur --voices-from en
stage experiment_chatter chatter generate.py $OTHER --voices-from en

# 5. Word checks on every test line folder.
for l in $OTHER ur; do
  for d in outputs/step1_$l/*(/N); do
    stage "check_lines_${l}_${d:t}" tool tools/check_clips.py $l lines $d
  done
done

print "$(date '+%H:%M') ALL DONE" >> "$LOG/overnight.log"
