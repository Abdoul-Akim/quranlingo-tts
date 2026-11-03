# Voice consistency: how close a clip's voice is to the reference voice it was cloned from.
# A voice encoder turns each recording into a "fingerprint" (an embedding); the cosine of two
# fingerprints is 1.0 for the same voice and lower the more the voices differ.
import numpy as np

from line_jobs import voice_path


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def reference_for(folder_name: str, language: str, character: str):
    # "voxcpm2" used the native voice; "voxcpm2_voice_en" was cloned from the English voice.
    voices_from = folder_name.split("_voice_")[1] if "_voice_" in folder_name else None
    return voice_path(language, character, voices_from)
