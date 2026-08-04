import { defineCollection } from "astro:content";
import { glob } from "astro/loaders";
import { z } from "astro/zod";

const lore = defineCollection({
  loader: glob({
    base: "./Torchbearer sessions/Lore",
    pattern: "**/*.md",
    retainBody: true
  }),
  schema: z.object({
      title: z.string(),
      publish: z.boolean().default(false),
      audience: z.string().optional(),
      status: z.string().optional(),
      certainty: z.string().optional(),
      lore_type: z.string().optional(),
      aliases: z.array(z.string()).optional(),
      tags: z.array(z.string()).optional()
    })
});

export const collections = { lore };
