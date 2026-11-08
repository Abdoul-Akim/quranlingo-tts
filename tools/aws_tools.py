# Helpers for the AWS listening site: upload the pages and rounds, and read the votes back.
# Uses the AWS command line (aws), logged in with the profile QuranLingo gives us.
#
# Run from the TTS folder:
#   python3 tools/aws_tools.py publish      upload pages and rounds, refresh the cache
#   python3 tools/aws_tools.py votes        download all votes to outputs/aws_votes.jsonl
# Settings: AWS_PROFILE (default quranlingo), AWS_REGION (default eu-central-1).
import json
import os
import subprocess
import sys
from pathlib import Path

TTS_DIR = Path(__file__).resolve().parents[1]
STACK_NAME = "quranlingo-voices"
PROFILE = os.environ.get("AWS_PROFILE", "quranlingo")
REGION = os.environ.get("AWS_REGION", "eu-central-1")
VOTES_FILE = TTS_DIR / "outputs" / "aws_votes.jsonl"


def stack_outputs(profile: str = PROFILE, region: str = REGION) -> dict:
    result = subprocess.run(
        ["aws", "cloudformation", "describe-stacks", "--stack-name", STACK_NAME, "--query", "Stacks[0].Outputs",
         "--output", "json", "--profile", profile, "--region", region],
        check=True, capture_output=True, text=True,
    )
    return {o["OutputKey"]: o["OutputValue"] for o in json.loads(result.stdout)}


def publish_commands(stack: dict, profile: str = PROFILE, region: str = REGION) -> list[list[str]]:
    # The answer keys (keys/) are never part of any upload.
    bucket, login = stack["BucketName"], ["--profile", profile, "--region", region]
    return [
        ["aws", "s3", "sync", "aws_site/web", f"s3://{bucket}", "--delete", "--exclude", "rounds/*", *login],
        ["aws", "s3", "sync", "listening_site/rounds", f"s3://{bucket}/rounds", "--delete",
         "--exclude", "*", "--include", "pages.json", "--include", "*/round.json", "--include", "*.wav", *login],
        ["aws", "cloudfront", "create-invalidation", "--distribution-id", stack["DistributionId"], "--paths", "/*",
         *login],
    ]


def _plain(value: dict):
    # One DynamoDB typed value ({"S": "x"}, {"L": [...]}, {"NULL": true}, ...) as plain Python.
    (kind, inner), = value.items()
    if kind == "NULL":
        return None
    if kind == "L":
        return [_plain(v) for v in inner]
    if kind == "M":
        return {k: _plain(v) for k, v in inner.items()}
    if kind == "N":
        return float(inner) if "." in inner else int(inner)
    return inner


def from_dynamodb(item: dict) -> dict:
    return {key: _plain(value) for key, value in item.items()}


def download_votes(stack: dict, profile: str = PROFILE, region: str = REGION) -> int:
    result = subprocess.run(
        ["aws", "dynamodb", "scan", "--table-name", stack["TableName"], "--output", "json",
         "--profile", profile, "--region", region],
        check=True, capture_output=True, text=True,
    )
    votes = [from_dynamodb(item) for item in json.loads(result.stdout)["Items"]]
    VOTES_FILE.parent.mkdir(parents=True, exist_ok=True)
    VOTES_FILE.write_text("".join(json.dumps(v, ensure_ascii=False) + "\n" for v in votes), encoding="utf-8")
    return len(votes)


if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else ""
    if action == "publish":
        for command in publish_commands(stack_outputs()):
            print("$", " ".join(command))
            subprocess.run(command, check=True, cwd=TTS_DIR)
        print("Published:", stack_outputs()["SiteUrl"])
    elif action == "votes":
        print(f"{download_votes(stack_outputs())} votes saved to {VOTES_FILE.relative_to(TTS_DIR)}")
    else:
        sys.exit("Use: python3 tools/aws_tools.py publish | votes")
