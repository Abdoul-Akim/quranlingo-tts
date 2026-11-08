# QuranLingo voices listening site on AWS

The blind listening test, rebuilt to run on QuranLingo's AWS account. It replaces the Gradio site on Render once it is live.

| Part | Where |
|---|---|
| Pages (`web/`) | plain HTML, CSS and JavaScript; one page per language, right to left for Arabic and Urdu |
| Audio and rounds | `listening_site/rounds/`, built by `tools/make_round.py` as before |
| Pages and audio online | private S3 bucket, served by CloudFront |
| Votes | `POST /api/vote` → Lambda (`api/votes.py`) → DynamoDB, one item per tester and question |
| Answer keys | `keys/`, on this computer only, never uploaded |

Testers' answers are saved one at a time, so nothing is lost if they leave halfway, and the page remembers their progress in the browser.

## Try it on this computer

```bash
python3 tools/serve_aws_site.py
```

Open http://localhost:8765. Votes go to `outputs/aws_local_votes.jsonl`.

## First deploy (once)

1. QuranLingo's AWS admin creates an IAM user for this project with the policy in `deploy_policy.json`, which only reaches resources named `quranlingo-voices-*`, and gives you an access key.
2. Log in once:
   ```bash
   aws configure --profile quranlingo
   ```
   Enter the access key, the secret key, region `eu-central-1` and output `json`.
3. Deploy:
   ```bash
   zsh tools/deploy_aws.sh
   ```
   The first run takes about 5 to 10 minutes (CloudFront is slow to create). It ends with the site's address.

## Every time rounds change

```bash
python3 tools/aws_tools.py publish
```

## Counting votes

```bash
uv run --project listening_site python tools/results.py --aws
```

## Tests

```bash
uv run --project analysis python -m pytest tests/test_aws_votes.py tests/test_aws_tools.py tests/test_serve_aws_site.py
node --test tests/web/*.test.mjs
```

## Cost

With fewer than 50 testers, close to nothing: DynamoDB and Lambda are billed per request, and S3 and CloudFront per gigabyte (about 300 MB of audio).
