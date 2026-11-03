#!/bin/zsh
# Follow-up to run_overnight.sh: consistency checks, variations, website rounds, Parler, report.
# Resumable like the overnight run; a failing stage is logged and the run carries on.
#
# Run from the TTS folder:  caffeinate -i zsh tools/run_after.sh
cd "${0:A:h}/.."
TTS="$PWD"
LOG="$TTS/outputs/logs"
mkdir -p "$LOG"
ALL=(en fr de tr ar hi ur)

stage() {  # stage <name> <command...>
  local name=$1; shift
  print "$(date '+%H:%M') start $name" >> "$LOG/after.log"
  if "$@" >> "$LOG/$name.log" 2>&1; then
    print "$(date '+%H:%M') done  $name" >> "$LOG/after.log"
  else
    print "$(date '+%H:%M') FAILED $name (see $name.log)" >> "$LOG/after.log"
  fi
}
vox()     { (cd "$TTS/engines/voxcpm2" && uv run python "$@") }
chatter() { (cd "$TTS/engines/chatterbox" && uv run python "$@") }
parler()  { (cd "$TTS/engines/parler" && uv run python "$@") }

# 1. Voice consistency for every test line folder.
for l in $ALL; do
  for d in outputs/step1_$l/*(/N); do
    stage "similarity_${l}_${d:t}" chatter speaker_similarity.py $l "$TTS/$d"
  done
done

# 2. Emotional variations, English first.
stage variations_vox_en     vox generate.py en --set variations
stage variations_chatter_en chatter generate.py en --set variations

# 3. Website rounds (make_round refuses to overwrite, so rerunning is safe).
for l in $ALL; do
  [[ -f outputs/base_voices/$l/checks.csv ]] && stage "round_base_$l" python3 tools/make_round.py base base_$l $l
  [[ -d outputs/step1_$l/chatterbox && -d outputs/step1_$l/voxcpm2 ]] && \
    stage "round_lines_$l" python3 tools/make_round.py engines lines_$l $l chatterbox voxcpm2
  [[ $l != en && -d outputs/step1_$l/voxcpm2_voice_en ]] && \
    stage "round_experiment_$l" python3 tools/make_round.py experiment experiment_$l $l voxcpm2 en
done

# 4. Urdu and Hindi with Indic Parler-TTS (fails until its terms are accepted on Hugging Face).
stage parler_base parler design_base_voices.py ur hi

# 5. The report.
stage report python3 tools/summarise.py
print "$(date '+%H:%M') ALL DONE" >> "$LOG/after.log"
