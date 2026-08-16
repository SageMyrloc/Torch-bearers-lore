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
    "# Torchbearers\n\n"
    "You are a member of a **Pathfinder Society expedition** sent through a newly discovered portal to explore a place from which no expedition has yet returned.\n\n"
    "The destination is the **Veil of Aeluran**, a mysterious demiplane believed to have been created by the ancient wizard **Aelthir Vaelorn**. His surviving research suggests that the Veil was created using an extraordinarily powerful artifact known as the **Gloamheart Prism**.\n\n"
    "The portal is **one-way**. Those who accepted the expedition knew that before they stepped through.\n\n"
    "## Beyond the Portal\n\n"
    "The Torchbearers emerge into the marketplace of an abandoned town.\n\n"
    "A great magical lantern burns at its centre, holding back the supernatural mist that fills the surrounding streets. Within its light is safety. Beyond it, doors and windows have been barricaded, the town lies silent, and things move in the mist.\n\n"
    "Smaller lanterns can carry that protection beyond the marketplace—but only for a limited time.\n\n"
    "For now, the marketplace is your foothold.\n\n"
    "Everything beyond it must be explored.\n\n"
    "## Your Purpose\n\n"
    "The Pathfinder Society has sent the Torchbearers to **explore the Veil, recover what has been lost, and discover what happened here**.\n\n"
    "Why was the Veil created?\n\n"
    "What became of Aelthir Vaelorn?\n\n"
    "Where is the Gloamheart Prism?\n\n"
    "What happened to the people who once lived in the abandoned town?\n\n"
    "And, perhaps most importantly:\n\n"
    "**Is there another way home?**\n\n"
    "---\n\n"
    "## Begin Here\n\n"
    "New to the campaign? Start with **[What Your Character Knows](<Golarion and the Pathfinder Society/What Your Character Knows.md>)**.\n\n"
    "From there, follow whichever part of the mystery interests you:\n\n"
    "- **[The Pathfinder Society Expedition](<Golarion and the Pathfinder Society/The Pathfinder Society Expedition.md>)** — why the Torchbearers crossed the portal.\n"
    "- **[The Veil of Aeluran](<The Plane/The Veil of Aeluran/The Veil of Aeluran.md>)** — the demiplane itself.\n"
    "- **[Aelthir Vaelorn](<The Plane/Aelthir Vaelorn/Aelthir Vaelorn.md>)** — the obscure wizard credited with creating it.\n"
    "- **[Aelthir Vaelorn's Research](<The Plane/Aelthir Vaelorn/Aelthir Vaelorn's Research.md>)** — what surviving scholarship suggests he was trying to achieve.\n"
    "- **[The Gloamheart Prism](<The Plane/The Gloamheart Prism/The Gloamheart Prism.md>)** — the artifact that powered the Veil's creation.\n\n"
    "## Current Situation\n\n"
    "- **[The Protected Marketplace](<The Plane/The Safe Town/The Protected Marketplace.md>)** — the expedition's safe foothold.\n"
    "- **[The Central Lantern](<The Plane/The Central Lantern/The Central Lantern.md>)** — the light holding back the mist.\n"
    "- **[Personal Lanterns](<The Plane/Personal Lanterns/Personal Lanterns.md>)** — how explorers travel beyond safety.\n"
    "- **[The Mist](<The Plane/The Mist/The Mist.md>)** — the greatest immediate danger.\n"
    "- **[The Barred Town](<The Plane/The Safe Town/The Barred Town.md>)** — the unreclaimed settlement beyond the square.\n",
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
