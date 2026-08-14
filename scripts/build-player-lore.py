from pathlib import Path
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

for source in SOURCE.rglob("*"):
    if not source.is_file() or source.suffix.lower() != ".md":
        continue
    relative = source.relative_to(SOURCE)
    target = DOCS / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    text = source.read_text(encoding="utf-8-sig")
    # Obsidian wikilinks are made readable by MkDocs while retaining their labels.
    text = re.sub(r"!??\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|([^\]]+))?\]\]", lambda m: m.group(2) or m.group(1), text)
    target.write_text(text, encoding="utf-8")

print(f"Built public docs from {SOURCE}")
