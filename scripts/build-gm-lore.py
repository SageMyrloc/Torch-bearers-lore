from pathlib import Path
import os
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
LORE = ROOT / "Torchbearer sessions" / "Lore"
PLAYER_SOURCE = LORE / "Player Knowledge"
GM_SOURCE = LORE / "GM Knowledge"
DOCS = ROOT / "gm-docs"

for source in (PLAYER_SOURCE, GM_SOURCE):
    if not source.is_dir():
        raise SystemExit(f"Required lore source not found: {source}")

# Safety invariant: the GM site is generated only from the two shared lore trees.
# Initial Sessions, Westmarch sessions, ChatGPT instructions and any other material
# outside Lore/Player Knowledge and Lore/GM Knowledge are deliberately excluded.
if PLAYER_SOURCE.parent != LORE or GM_SOURCE.parent != LORE:
    raise SystemExit("Refusing to build: unexpected GM lore source paths")

if DOCS.exists():
    shutil.rmtree(DOCS)
DOCS.mkdir()

(DOCS / "index.md").write_text(
    "# Torchbearers GM Archive\n\n"
    "This archive contains both player-facing lore and shared GM knowledge.\n\n"
    "It is intentionally separate from the public player archive.\n",
    encoding="utf-8",
)

source_groups = [
    ("Player Knowledge", PLAYER_SOURCE),
    ("GM Knowledge", GM_SOURCE),
]

sources: list[tuple[str, Path, Path]] = []
for section, root in source_groups:
    for source in root.rglob("*.md"):
        if source.is_file():
            relative = Path(section) / source.relative_to(root)
            sources.append((section, source, relative))

# Resolve Obsidian wikilinks across both shared lore trees.
link_targets: dict[str, Path] = {}
for _section, source, relative in sources:
    link_targets.setdefault(source.stem.casefold(), relative)
    text = source.read_text(encoding="utf-8-sig")
    title_match = re.search(r'^title:\s*["\']?(.+?)["\']?\s*$', text, re.MULTILINE)
    if title_match:
        link_targets.setdefault(title_match.group(1).casefold(), relative)


def convert_wikilinks(text: str, current_relative: Path) -> str:
    pattern = re.compile(r"(!?)\[\[([^\]|#]+)(?:#([^\]|]+))?(?:\|([^\]]+))?\]\]")

    def replace(match: re.Match[str]) -> str:
        target_name = match.group(2).strip()
        anchor = match.group(3)
        label = (match.group(4) or target_name).strip()
        target = link_targets.get(target_name.casefold())
        if target is None:
            return label

        relative_url = os.path.relpath(target, start=current_relative.parent).replace(os.sep, "/")
        if anchor:
            slug = re.sub(r"[^a-z0-9 -]", "", anchor.casefold()).strip().replace(" ", "-")
            relative_url += f"#{slug}"
        return f"[{label}]({relative_url})"

    return pattern.sub(replace, text)


def convert_callouts(text: str) -> str:
    lines = text.splitlines()
    output: list[str] = []
    i = 0

    while i < len(lines):
        match = re.match(r"^>\s*\[!([A-Za-z0-9_-]+)\](?:[+-])?\s*(.*)$", lines[i])
        if not match:
            output.append(lines[i])
            i += 1
            continue

        kind = match.group(1).casefold()
        title = match.group(2).strip()
        heading = f'!!! {kind}'
        if title:
            safe_title = title.replace('"', '\\"')
            heading += f' "{safe_title}"'
        output.append(heading)
        i += 1

        while i < len(lines) and lines[i].startswith(">"):
            body = re.sub(r"^>\s?", "", lines[i])
            output.append(f"    {body}" if body else "    ")
            i += 1

    return "\n".join(output) + ("\n" if text.endswith("\n") else "")


for _section, source, relative in sources:
    target = DOCS / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    text = source.read_text(encoding="utf-8-sig")
    text = convert_wikilinks(text, relative)
    text = convert_callouts(text)
    target.write_text(text, encoding="utf-8")

print(f"Built GM docs from {PLAYER_SOURCE} and {GM_SOURCE}")
