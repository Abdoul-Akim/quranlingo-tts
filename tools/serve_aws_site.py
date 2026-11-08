# Try the AWS listening site on this computer before deploying it.
#   Pages from aws_site/web/, rounds from listening_site/rounds/, and POST /api/vote runs the
#   real vote function (aws_site/api/votes.py), saving to outputs/aws_local_votes.jsonl.
#
# Run from the TTS folder:  python3 tools/serve_aws_site.py      then open http://localhost:8765
import json
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

TTS_DIR = Path(__file__).resolve().parents[1]
WEB = TTS_DIR / "aws_site" / "web"
ROUNDS = TTS_DIR / "listening_site" / "rounds"
VOTES = TTS_DIR / "outputs" / "aws_local_votes.jsonl"
PORT = 8765


def local_file(url_path: str) -> Path | None:
    # Maps a URL path to a file inside WEB or ROUNDS, or None if it would leave them.
    path = unquote(urlparse(url_path).path)
    root, rest = (ROUNDS, path[len("/rounds/"):]) if path.startswith("/rounds/") else (WEB, path.lstrip("/"))
    target = (root / (rest or "index.html")).resolve()
    return target if target.is_relative_to(root.resolve()) else None


class LocalTable:
    def put_item(self, Item):
        VOTES.parent.mkdir(parents=True, exist_ok=True)
        with VOTES.open("a", encoding="utf-8") as f:
            f.write(json.dumps(Item, ensure_ascii=False) + "\n")


class Handler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        target = local_file(path)
        return str(target) if target else str(WEB / "missing")

    def do_POST(self):
        sys.path.insert(0, str(TTS_DIR / "aws_site" / "api"))
        import votes

        length = int(self.headers.get("content-length", 0))
        event = {"rawPath": "/" + urlparse(self.path).path.lstrip("/"), "requestContext": {"http": {"method": "POST"}},
                 "body": self.rfile.read(length).decode("utf-8", "replace"), "isBase64Encoded": False}
        result = votes.handler(event, None, table=LocalTable())
        self.send_response(result["statusCode"])
        for name, value in result["headers"].items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(result["body"].encode("utf-8"))


if __name__ == "__main__":
    print(f"Open http://localhost:{PORT}  (votes go to {VOTES.relative_to(TTS_DIR)}; Ctrl+C stops)")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
