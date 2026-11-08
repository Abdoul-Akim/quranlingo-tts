import base64
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "aws_site" / "api"))
import votes  # noqa: E402

TESTER = "a" * 32


class FakeTable:
    # Stands in for the DynamoDB table: put_item replaces an item with the same keys.
    def __init__(self):
        self.items = {}

    def put_item(self, Item):
        self.items[(Item["tester_id"], Item["question"])] = Item


def vote(**overrides):
    body = {"page": "fr", "tester_id": TESTER, "nickname": " Amina ", "round": "base_fr", "item": "ali",
            "clips": ["0a1b2c3d", "4e5f6a7b", "8c9d0e1f"], "choice": "B", "comment": " nice "}
    body.update(overrides)
    return body


def post(body, table, encoded=False):
    raw = json.dumps(body)
    event = {"requestContext": {"http": {"method": "POST"}}, "rawPath": "/api/vote",
             "body": base64.b64encode(raw.encode()).decode() if encoded else raw, "isBase64Encoded": encoded}
    return votes.handler(event, None, table=table)


def test_a_vote_is_saved_with_the_chosen_clip_decoded():
    table = FakeTable()
    response = post(vote(), table)
    assert response["statusCode"] == 200
    (item,) = table.items.values()
    assert item["chosen_clip"] == "4e5f6a7b"  # B
    assert item["nickname"] == "Amina" and item["comment"] == "nice"
    assert item["question"] == "base_fr#ali" and item["time"]


def test_changing_an_answer_replaces_the_old_one():
    table = FakeTable()
    post(vote(choice="A"), table)
    post(vote(choice="same"), table)
    (item,) = table.items.values()
    assert item["choice"] == "same" and item["chosen_clip"] is None


def test_up_to_five_takes_can_be_compared():
    table = FakeTable()
    clips = ["0a1b2c3d", "4e5f6a7b", "8c9d0e1f", "11111111", "22222222"]
    assert post(vote(clips=clips, choice="E"), table)["statusCode"] == 200
    assert table.items[(TESTER, "base_fr#ali")]["chosen_clip"] == "22222222"


def test_base64_bodies_are_read():
    # CloudFront and function URLs may pass the body base64 encoded.
    table = FakeTable()
    assert post(vote(), table, encoded=True)["statusCode"] == 200


def test_bad_votes_are_refused_and_not_saved():
    table = FakeTable()
    bad = [
        vote(choice="D"),  # only three clips
        vote(clips=["0a1b2c3d"]),  # one clip
        vote(clips=["../../etc"] * 2),  # not a clip name
        vote(tester_id="x"),
        vote(round="base fr; drop"),
        vote(comment="x" * 2001),
        vote(nickname="x" * 61),
    ]
    for body in bad:
        assert post(body, table)["statusCode"] == 400, body
    assert table.items == {}


def test_only_post_to_the_vote_path_is_accepted():
    table = FakeTable()
    event = {"requestContext": {"http": {"method": "GET"}}, "rawPath": "/api/vote", "body": ""}
    assert votes.handler(event, None, table=table)["statusCode"] == 405
    event = {"requestContext": {"http": {"method": "POST"}}, "rawPath": "/api/other", "body": "{}"}
    assert votes.handler(event, None, table=table)["statusCode"] == 404


def test_broken_json_is_refused():
    event = {"requestContext": {"http": {"method": "POST"}}, "rawPath": "/api/vote", "body": "{"}
    assert votes.handler(event, None, table=FakeTable())["statusCode"] == 400
