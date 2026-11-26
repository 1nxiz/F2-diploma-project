#!/usr/bin/env python3
"""Check relative links and #anchors between Markdown files in docs/.

GitHub-style anchors are generated for headings; explicit <a id="..."> anchors
are collected as well. External (http/https/mailto) links are skipped.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"


def slug(heading: str) -> str:
    text = re.sub(r"`([^`]*)`", r"\1", heading.strip().lower())
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


def anchors(path: Path) -> set[str]:
    result, seen = set(), {}
    in_code = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        result.update(re.findall(r'<a id="([^"]+)"', line))
        m = re.match(r"^#{1,6} (.+)$", line)
        if m:
            s = slug(m.group(1))
            n = seen.get(s, 0)
            seen[s] = n + 1
            result.add(s if n == 0 else f"{s}-{n}")
    return result


errors, total = [], 0
cache: dict[Path, set[str]] = {}
for md in sorted(DOCS.rglob("*.md")):
    text = re.sub(r"```.*?```", "", md.read_text(encoding="utf-8"), flags=re.S)
    for target in re.findall(r"\]\(([^)\s]+)\)", text):
        if re.match(r"^(https?|mailto):", target):
            continue
        total += 1
        file_part, _, frag = target.partition("#")
        dest = (md.parent / file_part).resolve() if file_part else md
        if not dest.exists():
            errors.append(f"{md.relative_to(ROOT)}: missing file {target}")
            continue
        if frag and dest.suffix == ".md":
            if dest not in cache:
                cache[dest] = anchors(dest)
            if frag not in cache[dest]:
                errors.append(f"{md.relative_to(ROOT)}: missing anchor {target}")

print("\n".join(errors) if errors else "")
print(f"Checked {total} relative links, {len(errors)} broken")
sys.exit(1 if errors else 0)
