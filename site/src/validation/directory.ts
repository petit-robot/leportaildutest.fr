import { z } from "zod";
import { DEFAULT_STATUS, STATUSES } from "@lib/status";

export const directorySchema = (imageSchema: z.ZodTypeAny) =>
  z.object({
    title: z.string().optional(),
    description: z.string().optional(),
    tags: z.array(z.string()).optional(),
    icon: z.string().optional(),
    image: imageSchema.optional(),
    link: z.string().url().optional(),
    featured: z.boolean().default(false),
    paid: z.boolean().default(false),
    status: z.enum(STATUSES).default(DEFAULT_STATUS),
  });