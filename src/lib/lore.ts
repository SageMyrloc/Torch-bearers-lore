import type { CollectionEntry } from "astro:content";

export type LoreEntry = CollectionEntry<"lore">;

const forbiddenPathParts = [
  "/antagonists/",
  "/initial sessions/",
  "/session plans/",
  "/chatgpt scope and instructions/"
];

const forbiddenSecretTerms = [
  "worm-that-walks",
  "worm that walks",
  "reanimated wizard",
  "reanimated corpse"
];

export function slugify(value: string) {
  return value
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/&/g, " and ")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "");
}

export function entryTitle(entry: LoreEntry) {
  return entry.data.title || entry.id.split("/").at(-1)?.replace(/\.md$/i, "") || "Untitled";
}

export function entrySlug(entry: LoreEntry) {
  return slugify(entryTitle(entry));
}

export function entryAudience(entry: LoreEntry) {
  return entry.data.audience?.toLowerCase() === "gm" ? "GM lore" : "Player knowledge";
}

export function isPublishable(entry: LoreEntry) {
  const path = `/${entry.id.toLowerCase()}/`;
  const body = (entry.body || "").toLowerCase();

  return (
    entry.data.publish === true &&
    entry.data.status?.toLowerCase() !== "deprecated" &&
    !forbiddenPathParts.some((part) => path.includes(part)) &&
    !forbiddenSecretTerms.some((term) => body.includes(term))
  );
}

export function publishedLore(entries: LoreEntry[]) {
  return entries
    .filter(isPublishable)
    .sort((a, b) => entryTitle(a).localeCompare(entryTitle(b), "en-GB"));
}

export function loreUrl(entry: LoreEntry, base: string) {
  return `${base}lore/${entrySlug(entry)}/`;
}
