# The owner's decisions by ear. Change this file after each listening session, then run
#   caffeinate -i zsh tools/run.sh pick,lines,similarity,rounds <languages>

# Takes the owner shortlisted by ear, per language and character. The first one becomes the
# reference voice in voices/<lang>/, and testers choose among all of them. Characters missing
# here keep the automatic pick (tools/rank_takes.py).
OWNER_SHORTLIST = {
    "en": {
        "ali": ["ali/v6_seed2.wav", "ali/v4_seed6.wav"],
        "fatima": ["fatima/v3_seed3.wav", "fatima/v3_seed2.wav", "fatima/v4_seed6.wav"],
        "omar": ["omar/v4_seed5.wav", "omar/v3_seed2.wav"],
        "zahra": ["zahra/v4_seed7.wav", "zahra/v6_seed4.wav", "zahra/v2_seed5.wav"],
    },
    # Owner's picks 2026-11-08. The take designed for Omar as omar/v3_seed2 sounds like a woman,
    # so it is Fatima's French voice.
    "fr": {
        "fatima": ["omar/v3_seed2.wav", "fatima/v3_seed2.wav"],
        "omar": ["omar/v4_seed1.wav", "omar/v4_seed2.wav", "omar/v4_seed3.wav"],
        "zahra": ["zahra/v4_seed2.wav", "zahra/v6_seed2.wav"],
    },
    "ar": {
        "fatima": ["fatima/v3_seed2.wav", "fatima/v4_seed1.wav", "fatima/v4_seed2.wav", "fatima/v4_seed3.wav"],
        "omar": ["omar/v3_seed1.wav", "omar/v3_seed2.wav", "omar/v4_seed1.wav"],
        "zahra": ["zahra/v4_seed2.wav", "zahra/v6_seed2.wav"],
    },
    "de": {
        "fatima": ["fatima/v3_seed2.wav", "fatima/v4_seed2.wav", "fatima/v4_seed3.wav"],
        "omar": ["omar/v3_seed2.wav", "omar/v3_seed3.wav", "omar/v4_seed2.wav"],
        "zahra": ["zahra/v4_seed2.wav", "zahra/v4_seed1.wav"],
    },
}

# Characters who keep one voice in every language: the English voice is cloned into the others
# (owner, 2026-11-08: the English Ali speaking French and Arabic beat every native Ali take).
SAME_VOICE_EVERYWHERE = {"ali": "en"}
