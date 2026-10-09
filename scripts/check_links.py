"""Phase H5: every link and image in README.md and DEMO.md must resolve (relative paths exist; web links answer)."""
import re
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)\)")
AUTO = re.compile(r"<(https?://[^>]+)>")


def links(path: Path) -> list[str]:
    text = path.read_text()
    return sorted(set(LINK.findall(text)) | set(AUTO.findall(text)))


def check_web(url: str) -> str:
    for method in ("HEAD", "GET"):
        try:
            request = Request(url, method=method, headers={"User-Agent": "Mozilla/5.0 (link check)"})
            with urlopen(request, timeout=30) as response:
                return f"ok {response.status}"
        except HTTPError as exc:
            if method == "GET":
                return f"blocked {exc.code}" if exc.code in {401, 403, 429, 999} else f"FAIL {exc.code}"
        except (URLError, TimeoutError, OSError) as exc:
            if method == "GET":
                return f"FAIL {type(exc).__name__}"
    return "FAIL"


def main(files=("README.md", "DEMO.md")) -> int:
    bad = 0
    for name in files:
        for target in links(ROOT / name):
            if target.startswith(("http://", "https://")):
                status = check_web(target)
            elif target.startswith("#"):
                status = "ok anchor"
            else:
                status = "ok file" if (ROOT / target.split("#")[0]).exists() else "FAIL missing file"
            bad += status.startswith("FAIL")
            print(f"{name}: {target} -> {status}")
    return bad


if __name__ == "__main__":
    sys.exit(bool(main()))
