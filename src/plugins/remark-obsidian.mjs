function slugify(value) {
  return value
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/&/g, " and ")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "");
}

function replaceWikilinks(node, base) {
  if (!node?.children || ["link", "code", "inlineCode"].includes(node.type)) return;

  node.children = node.children.flatMap((child) => {
    if (child.type !== "text") {
      replaceWikilinks(child, base);
      return child;
    }

    const parts = [];
    const pattern = /\[\[([^\]|]+)(?:\|([^\]]+))?\]\]/g;
    let cursor = 0;
    let match;

    while ((match = pattern.exec(child.value)) !== null) {
      if (match.index > cursor) parts.push({ type: "text", value: child.value.slice(cursor, match.index) });
      const target = match[1].trim();
      const label = (match[2] || target).trim();
      parts.push({
        type: "link",
        url: `${base}lore/${slugify(target)}/`,
        children: [{ type: "text", value: label }]
      });
      cursor = pattern.lastIndex;
    }

    if (!parts.length) return child;
    if (cursor < child.value.length) parts.push({ type: "text", value: child.value.slice(cursor) });
    return parts;
  });
}

function styleCallouts(node) {
  if (!node?.children) return;

  if (node.type === "blockquote") {
    const paragraph = node.children[0];
    const first = paragraph?.children?.[0];
    const match = first?.type === "text" && first.value.match(/^\[!([a-z-]+)\]\s*/i);
    if (match) {
      node.data = node.data || {};
      node.data.hProperties = node.data.hProperties || {};
      node.data.hProperties.className = ["callout", `callout-${match[1].toLowerCase()}`];
      first.value = first.value.slice(match[0].length);
    }
  }

  node.children.forEach(styleCallouts);
}

export default function remarkObsidian(options = {}) {
  const base = options.base || "/";
  return (tree) => {
    replaceWikilinks(tree, base);
    styleCallouts(tree);
  };
}
