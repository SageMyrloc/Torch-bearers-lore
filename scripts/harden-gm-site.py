from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site" / "archive-4d7c9e2b6f1a"

if not SITE.is_dir():
    raise SystemExit(f"GM site output not found: {SITE}")

for sitemap in (SITE / "sitemap.xml", SITE / "sitemap.xml.gz"):
    if sitemap.exists():
        sitemap.unlink()

marker = '<meta name="robots" content="noindex, nofollow, noarchive">'
for html_file in SITE.rglob("*.html"):
    text = html_file.read_text(encoding="utf-8")
    if marker not in text:
        text = text.replace("</head>", f"  {marker}\n</head>", 1)
        html_file.write_text(text, encoding="utf-8")

print(f"Hardened hidden GM site at {SITE}")
