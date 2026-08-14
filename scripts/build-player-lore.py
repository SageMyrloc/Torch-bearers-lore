from pathlib import Path
import os
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "Torchbearer sessions" / "Lore" / "Player Knowledge"
DOCS = ROOT / "docs"

if not SOURCE.is_dir():
    raise SystemExit(f"Player Knowledge source not found: {SOURCE}")

# Safety invariant: the public site is generated exclusively from Player Knowledge.
# Never broaden SOURCE to Lore/ or the repository root: GM Knowledge must not be published.
if SOURCE.name != "Player Knowledge" or SOURCE.parent.name != "Lore":
    raise SystemExit("Refusing to build: unexpected player lore source path")

if DOCS.exists():
    shutil.rmtree(DOCS)
DOCS.mkdir()

(DOCS / "index.md").write_text(
    "# Torchbearers Lore\n\n"
    "Welcome to the expedition archive. This site contains knowledge available to players.\n\n"
    "Use the navigation or search to explore what the expedition currently knows.\n",
    encoding="utf-8",
)

sources = [
    source
    for source in SOURCE.rglob("*.md")
    if source.is_file()
]

# Resolve Obsidian wikilinks by both filename and front-matter title.
# Only Player Knowledge files are indexed, so links can never expose GM-only pages.
link_targets: dict[str, Path] = {}
for source in sources:
    relative = source.relative_to(SOURCE)
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

        # If a player-safe target does not exist, keep readable text rather than
        # creating a broken link or searching outside Player Knowledge.
        if target is None:
            return label

        relative_url = os.path.relpath(target, start=current_relative.parent).replace(os.sep, "/")
        if anchor:
            slug = re.sub(r"[^a-z0-9 -]", "", anchor.casefold()).strip().replace(" ", "-")
            relative_url += f"#{slug}"
        return f"[{label}]({relative_url})"

    return pattern.sub(replace, text)


def convert_callouts(text: str) -> str:
    """Convert Obsidian callouts into MkDocs Material admonitions."""
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


for source in sources:
    relative = source.relative_to(SOURCE)
    target = DOCS / relative
    target.parent.mkdir(parents=True, exist_ok=True)

    text = source.read_text(encoding="utf-8-sig")
    text = convert_wikilinks(text, relative)
    text = convert_callouts(text)
    target.write_text(text, encoding="utf-8")

print(f"Built public docs from {SOURCE}")
