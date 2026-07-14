#!/usr/bin/env python3
"""Regenerate changelog/<year>.mdx pages from usertour/usertour GitHub releases.

Usage: python3 scripts/sync-changelog.py  (requires the `gh` CLI, logged in)

Fetches every release, groups them by year, and rewrites one MDX page per
year using Mintlify <Update> components. If a new year appears, add
"changelog/<year>" to the Changelog group in docs.json.
"""

import json
import os
import re
import subprocess
from collections import defaultdict
from datetime import datetime

REPO = "usertour/usertour"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DST_DIR = os.path.join(ROOT, "changelog")


def fetch_releases():
    out = subprocess.run(
        ["gh", "api", f"repos/{REPO}/releases", "--paginate"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    releases = json.loads(out)
    releases = [r for r in releases if not r["draft"] and not r["prerelease"]]
    releases.sort(key=lambda r: r["published_at"], reverse=True)
    return releases


def escape_mdx(text):
    """Escape <, {, } outside code fences and inline code spans so MDX compiles."""
    out = []
    in_fence = False
    for line in text.split("\n"):
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            out.append(line)
            continue
        if in_fence:
            out.append(line)
            continue
        parts = re.split(r"(`+[^`]+`+)", line)
        rebuilt = []
        for p in parts:
            if p.startswith("`"):
                rebuilt.append(p)
            else:
                p = p.replace("{", "\\{").replace("}", "\\}").replace("<", "\\<")
                rebuilt.append(p)
        out.append("".join(rebuilt))
    return "\n".join(out)


def clean_body(body, html_url):
    if not body or not body.strip():
        return f"See the [release notes on GitHub]({html_url})."
    body = body.replace("\r\n", "\n").strip()
    # Drop the boilerplate "## What's Changed" heading; the ### sections
    # beneath it carry the real titles (and make better RSS entries).
    body = re.sub(r"^##\s+What'?s Changed\s*$\n?", "", body, flags=re.MULTILINE)
    body = re.sub(r"\n{3,}", "\n\n", body).strip()
    return escape_mdx(body)


def main():
    by_year = defaultdict(list)
    for r in fetch_releases():
        date = datetime.strptime(r["published_at"], "%Y-%m-%dT%H:%M:%SZ")
        desc = f"{date.strftime('%B')} {date.day}, {date.year}"
        body = clean_body(r["body"], r["html_url"])
        by_year[date.year].append(
            f'<Update label="{r["tag_name"]}" description="{desc}">\n\n{body}\n\n</Update>'
        )

    os.makedirs(DST_DIR, exist_ok=True)
    years = sorted(by_year, reverse=True)
    for year in years:
        frontmatter = f"""---
title: "{year}"
description: "Usertour releases in {year}"
rss: true
---
"""
        path = os.path.join(DST_DIR, f"{year}.mdx")
        with open(path, "w") as f:
            f.write(frontmatter + "\n" + "\n\n".join(by_year[year]) + "\n")
        print(f"wrote {os.path.relpath(path, ROOT)} with {len(by_year[year])} entries")

    with open(os.path.join(ROOT, "docs.json")) as f:
        nav = f.read()
    missing = [y for y in years if f"changelog/{y}" not in nav]
    if missing:
        print(f"NOTE: add {['changelog/' + str(y) for y in missing]} to the Changelog group in docs.json")


if __name__ == "__main__":
    main()
