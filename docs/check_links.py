"""Check local inline Markdown link targets. Read-only; no network requests."""

import json
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]


def main():
    names = subprocess.check_output(
        ["git", "--no-optional-locks", "ls-files", "-z", "--cached", "--others",
         "--exclude-standard"], cwd=ROOT,
    ).decode().split("\0")
    checked = 0
    missing = []
    for name in sorted(set(names)):
        source = ROOT / name
        if source.suffix != ".md" or not source.is_file():
            continue
        text = re.sub(r"```.*?```", "", source.read_text(), flags=re.S)
        for match in re.finditer(r"\]\((<[^>]+>|[^\s)]+)(?:\s+[^)]*)?\)", text):
            target = match[1].strip("<>")
            url = urlsplit(target)
            if url.scheme or url.netloc or not url.path:
                continue
            path = unquote(url.path)
            destination = (ROOT / path.lstrip("/") if path.startswith("/")
                           else source.parent / path)
            checked += 1
            if not destination.exists():
                missing.append({"source": name, "target": target})
    print(json.dumps({"local_file_targets_checked": checked, "missing": missing,
                      "scope": "inline Markdown file targets; not anchors or external URLs"},
                     indent=2))
    return bool(missing)


if __name__ == "__main__":
    raise SystemExit(main())