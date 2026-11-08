# Saves one listening test answer to DynamoDB. Runs as an AWS Lambda function behind
# CloudFront at POST /api/vote. One item per tester and question, so changing an answer
# (or adding a comment later) replaces the old one.
import base64
import json
import os
import re
from datetime import datetime, timezone

LETTERS = "ABCDE"
CLIP = re.compile(r"^[0-9a-f]{8}$")  # make_round.py names clips with 8 random hex characters
TESTER = re.compile(r"^[0-9a-f]{32}$")
NAME = re.compile(r"^[A-Za-z0-9_-]{1,64}$")  # rounds and items, e.g. base_fr, q04_opt2
PAGE = re.compile(r"^[A-Za-z0-9_-]{0,16}$")
MAX_NICKNAME, MAX_COMMENT = 60, 2000

_table = None


def _default_table():
    global _table
    if _table is None:
        import boto3  # included in the Lambda runtime
        _table = boto3.resource("dynamodb").Table(os.environ["TABLE_NAME"])
    return _table


def _response(status: int, body: dict) -> dict:
    return {"statusCode": status, "headers": {"content-type": "application/json", "cache-control": "no-store"},
            "body": json.dumps(body)}


def parse_vote(body: dict) -> dict:
    # Returns the item to save, or raises ValueError with the reason.
    clips = body.get("clips")
    if not isinstance(clips, list) or not 2 <= len(clips) <= len(LETTERS):
        raise ValueError("clips")
    if not all(isinstance(c, str) and CLIP.match(c) for c in clips):
        raise ValueError("clips")
    choice = body.get("choice")
    letters = LETTERS[: len(clips)]
    if choice != "same" and (not isinstance(choice, str) or choice not in letters or len(choice) != 1):
        raise ValueError("choice")
    fields = {name: body.get(name) for name in ("page", "tester_id", "round", "item")}
    checks = {"page": PAGE, "tester_id": TESTER, "round": NAME, "item": NAME}
    for name, pattern in checks.items():
        if not isinstance(fields[name], str) or not pattern.match(fields[name]):
            raise ValueError(name)
    nickname, comment = body.get("nickname") or "", body.get("comment") or ""
    if not isinstance(nickname, str) or len(nickname.strip()) > MAX_NICKNAME:
        raise ValueError("nickname")
    if not isinstance(comment, str) or len(comment.strip()) > MAX_COMMENT:
        raise ValueError("comment")
    nickname, comment = nickname.strip(), comment.strip()
    return {
        **fields,
        "question": f"{fields['round']}#{fields['item']}",
        "time": datetime.now(timezone.utc).isoformat(),
        "nickname": nickname,
        "clips": clips,  # in the order shown: A, B, ...
        "choice": choice,  # a letter or "same"
        "chosen_clip": None if choice == "same" else clips[letters.index(choice)],
        "comment": comment,
    }


def handler(event, context, table=None):
    if event.get("rawPath") != "/api/vote":
        return _response(404, {"error": "not found"})
    if event.get("requestContext", {}).get("http", {}).get("method") != "POST":
        return _response(405, {"error": "use POST"})
    raw = event.get("body") or ""
    try:
        if event.get("isBase64Encoded"):
            raw = base64.b64decode(raw).decode("utf-8")
        body = json.loads(raw)
        if not isinstance(body, dict):
            raise ValueError("body")
        item = parse_vote(body)
    except (ValueError, UnicodeDecodeError) as error:
        return _response(400, {"error": f"bad {error}"})
    (table or _default_table()).put_item(Item=item)
    return _response(200, {"ok": True})
