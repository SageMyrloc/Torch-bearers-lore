import { defineConfig } from "astro/config";
import { unified } from "@astrojs/markdown-remark";
import remarkObsidian from "./src/plugins/remark-obsidian.mjs";

export default defineConfig({
  site: "https://sagemyrloc.github.io",
  base: "/Torch-bearers-lore",
  trailingSlash: "always",
  markdown: {
    processor: unified({
      remarkPlugins: [[remarkObsidian, { base: "/Torch-bearers-lore/" }]],
      shikiConfig: { theme: "github-dark" }
    })
  },
  vite: {
    build: { cssMinify: true }
  }
});
