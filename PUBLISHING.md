# Publishing lore

The website builds from Markdown in `Torchbearer sessions/Lore`.

Add this property to an article's YAML frontmatter when it is safe to publish:

```yaml
publish: true
```

New articles remain unpublished by default. The build also rejects deprecated articles, session material, antagonist files, scope documents, and articles containing the reserved Worm That Walks terminology. These exclusions are a safety net; sensitive material should still omit `publish: true`.

Merging to `main` triggers the GitHub Pages deployment. In the repository settings, select **GitHub Actions** as the Pages source the first time the site is enabled.
