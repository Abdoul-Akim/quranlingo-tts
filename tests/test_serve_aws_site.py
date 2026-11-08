from serve_aws_site import TTS_DIR, local_file

WEB = TTS_DIR / "aws_site" / "web"
ROUNDS = TTS_DIR / "listening_site" / "rounds"


def test_pages_come_from_the_web_folder():
    assert local_file("/") == WEB / "index.html"
    assert local_file("/app.js") == WEB / "app.js"


def test_rounds_come_from_the_listening_site_rounds():
    assert local_file("/rounds/base_en/round.json") == ROUNDS / "base_en" / "round.json"


def test_nothing_outside_those_folders_is_served():
    # The answer keys live in keys/, next to these folders; they must never be reachable.
    assert local_file("/rounds/../../keys/base_en.json") is None
    assert local_file("/../keys/base_en.json") is None
    assert local_file("/%2e%2e/keys/base_en.json") is None
