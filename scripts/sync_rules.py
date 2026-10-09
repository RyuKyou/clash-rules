#!/usr/bin/env python3
"""Download upstream rule-providers into rules/ and write index."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "sources.txt"
OUT_DIR = ROOT / "rules"
META = ROOT / "sync_meta.txt"


def load_sources() -> list[tuple[str, str, str]]:
    items = []
    for line in SOURCES.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 2:
            continue
        name, url = parts[0], parts[1]
        behavior = parts[2] if len(parts) > 2 else "classical"
        items.append((name, url, behavior))
    return items


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    sources = load_sources()
    ok, fail = [], []

    for name, url, behavior in sources:
        path = OUT_DIR / name
        try:
            print(f"GET {url}")
            r = requests.get(url, timeout=60)
            r.raise_for_status()
            data = r.content
            if not data:
                raise ValueError("empty body")
            path.write_bytes(data)
            digest = hashlib.sha256(data).hexdigest()[:12]
            ok.append(f"{name}\t{len(data)}\t{digest}\t{behavior}\t{url}")
            print(f"  OK {name} ({len(data)} bytes)")
        except Exception as e:
            fail.append(f"{name}\tFAIL\t{e}\t{url}")
            print(f"  FAIL {name}: {e}")
            # keep previous file if any

    now = datetime.now(timezone.utc).isoformat()
    lines = [
        f"updated={now}",
        f"ok={len(ok)}",
        f"fail={len(fail)}",
        "",
        "# name\tsize\tsha12\tbehavior\tupstream",
        *ok,
        "",
        "# failures",
        *fail,
        "",
    ]
    META.write_text("\n".join(lines), encoding="utf-8")

    # human-readable index for clients
    index = [
        "# Ryukyou clash-rules mirror",
        f"# updated: {now}",
        f"# success: {len(ok)}  failed: {len(fail)}",
        "",
        "# Local raw URL pattern:",
        "# https://raw.githubusercontent.com/RyuKyou/clash-rules/main/rules/<filename>",
        "# Mirror (CN-friendly):",
        "# https://cdn.jsdelivr.net/gh/RyuKyou/clash-rules@main/rules/<filename>",
        "",
    ]
    for name, url, behavior in sources:
        local = f"rules/{name}"
        status = "OK" if any(x.startswith(name + "\t") for x in ok) else "FAIL"
        index.append(f"{status}\t{behavior}\t{local}\t<-\t{url}")
    (ROOT / "INDEX.txt").write_text("\n".join(index) + "\n", encoding="utf-8")
    print(f"Done. ok={len(ok)} fail={len(fail)}")
    if not ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
