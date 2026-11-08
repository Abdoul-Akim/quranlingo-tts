from aws_tools import from_dynamodb, publish_commands

STACK = {"BucketName": "site-bucket", "DistributionId": "E123"}


def test_publish_uploads_the_pages_and_only_round_files():
    commands = publish_commands(STACK, profile="quranlingo", region="eu-central-1")
    flat = [" ".join(c) for c in commands]
    assert any("aws_site/web s3://site-bucket" in c for c in flat)
    rounds = next(c for c in commands if "s3://site-bucket/rounds" in c)
    # Everything is excluded first, then only what testers need is let through.
    assert rounds[rounds.index("--exclude") + 1] == "*"
    includes = [rounds[i + 1] for i, a in enumerate(rounds) if a == "--include"]
    assert sorted(includes) == ["*.wav", "*/round.json", "pages.json"]
    assert all("--profile" in c and "quranlingo" in c for c in commands)


def test_publish_never_touches_the_keys_and_refreshes_the_cache():
    commands = publish_commands(STACK, profile="p", region="r")
    assert not any("keys" in part for c in commands for part in c)
    last = commands[-1]
    assert last[:3] == ["aws", "cloudfront", "create-invalidation"] and "E123" in last


def test_dynamodb_items_become_plain_votes():
    item = {
        "tester_id": {"S": "abc"}, "round": {"S": "base_en"}, "item": {"S": "ali"},
        "clips": {"L": [{"S": "0a1b2c3d"}, {"S": "4e5f6a7b"}]}, "choice": {"S": "same"},
        "chosen_clip": {"NULL": True}, "nickname": {"S": ""}, "comment": {"S": "ok"},
    }
    vote = from_dynamodb(item)
    assert vote["clips"] == ["0a1b2c3d", "4e5f6a7b"] and vote["chosen_clip"] is None
    assert vote["choice"] == "same" and vote["comment"] == "ok"
