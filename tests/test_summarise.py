from summarise import engine_scores, markdown_table


def test_engine_scores_average_word_errors_and_count_bad_clips():
    checks = [{"clip": "e01.wav", "cer": "0.00"}, {"clip": "e02.wav", "cer": "0.20"}, {"clip": "e03.wav", "cer": "0.04"}]
    similarity = [{"clip": "e01.wav", "similarity": "0.90"}, {"clip": "e02.wav", "similarity": "0.80"}]
    scores = engine_scores(checks, similarity)
    assert scores["clips"] == 3
    assert scores["mean_cer"] == 0.08
    assert scores["bad_clips"] == 1  # above the 0.10 limit
    assert scores["mean_similarity"] == 0.85


def test_engine_scores_without_similarity_data():
    scores = engine_scores([{"clip": "e01.wav", "cer": "0.05"}], [])
    assert scores["mean_similarity"] is None


def test_markdown_table():
    table = markdown_table(["Language", "Clips"], [["en", 16], ["fr", None]])
    assert table.splitlines() == ["| Language | Clips |", "|---|---|", "| en | 16 |", "| fr |  |"]
