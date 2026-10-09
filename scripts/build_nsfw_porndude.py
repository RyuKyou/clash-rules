#!/usr/bin/env python3
"""
Build Clash classical rule-provider from Porndude-derived site lists.
Primary source: github.com/levelel/porndude_site_list (URLs scraped from theporndude.com/zh).
Also merges a few well-known tube CDN suffixes so media assets match, not only homepage HTML.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import requests

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "rules" / "NSFW_porndude.yaml"

LIST_URLS = [
    "https://raw.githubusercontent.com/levelel/porndude_site_list/main/zh.txt",
]

# Extra CDN / mirror hosts often needed after HTML loads (partial-load fix)
EXTRA_SUFFIXES = [
    "xhamster.com",
    "xhcdn.com",
    "xhwebsite.com",
    "pornhub.com",
    "phncdn.com",
    "pornhubpremium.com",
    "xvideos.com",
    "xvideos-cdn.com",
    "xnxx.com",
    "xnxx-cdn.com",
    "spankbang.com",
    "sb-cd.com",
    "redtube.com",
    "youporn.com",
    "tube8.com",
    "beeg.com",
    "hqporner.com",
    "eporner.com",
    "dood.video",
    "doodstream.com",
]

SKIP_SUFFIXES = (
    "google.com",
    "googleapis.com",
    "gstatic.com",
    "cloudflare.com",
    "cloudflareinsights.com",
    "facebook.com",
    "twitter.com",
    "x.com",
    "instagram.com",
    "theporndude.com",
    "porndude.link",
    "pdude.link",
    "w3.org",
    "schema.org",
)


def host_from_line(line: str) -> str | None:
    line = line.strip()
    if not line or line.startswith("#"):
        return None
    if "://" not in line:
        line = "http://" + line
    try:
        host = urlparse(line).hostname
    except Exception:
        return None
    if not host:
        return None
    host = host.lower().strip(".")
    if host.startswith("www."):
        host = host[4:]
    if "." not in host or any(c not in "abcdefghijklmnopqrstuvwxyz0123456789.-" for c in host):
        return None
    for skip in SKIP_SUFFIXES:
        if host == skip or host.endswith("." + skip):
            return None
    return host


def registrable_hint(host: str) -> str:
    """Prefer eTLD+1-ish: keep last two labels (good enough for rule lists)."""
    parts = host.split(".")
    if len(parts) >= 2:
        # co.uk style not handled; adult lists rarely need it
        return ".".join(parts[-2:])
    return host


def main() -> None:
    hosts: set[str] = set()
    for url in LIST_URLS:
        print(f"GET {url}")
        r = requests.get(url, timeout=60)
        r.raise_for_status()
        for line in r.text.splitlines():
            h = host_from_line(line)
            if h:
                hosts.add(h)
                hosts.add(registrable_hint(h))

    for h in EXTRA_SUFFIXES:
        hosts.add(h.lower())

    # drop junk single-label
    hosts = {h for h in hosts if h.count(".") >= 1}
    ordered = sorted(hosts)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        f"# NSFW domains derived from Porndude site lists",
        f"# generated: {now}",
        f"# count: {len(ordered)}",
        f"# sources: {', '.join(LIST_URLS)}",
        "# behavior: classical",
        "",
    ]
    for h in ordered:
        lines.append(f"DOMAIN-SUFFIX,{h}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT} ({len(ordered)} DOMAIN-SUFFIX rules)")


if __name__ == "__main__":
    main()
