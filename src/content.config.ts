import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

// Case studies live as MDX in src/content/work/*.mdx.
// The prose (Context, Process, Solution, ...) is the MDX body; everything a
// card or the page header needs comes from this frontmatter schema.
const work = defineCollection({
  loader: glob({ pattern: '**/*.mdx', base: './src/content/work' }),
  schema: z.object({
    title: z.string(),
    // One-line hook — the sentence that makes someone click in.
    hook: z.string(),
    // Teaser used on the home page card (falls back to hook if omitted).
    summary: z.string().optional(),
    // Hero meta grid
    role: z.string(),
    timeline: z.string(),
    team: z.string(),
    focus: z.string(),
    // The number/outcome you lead with. Optional while results are pending.
    keyResult: z.string().optional(),
    // In `minimal` mode's 4-pill meta grid, show "My focus" instead of
    // "Key result" as the 4th pill even when keyResult is set.
    metaPreferFocus: z.boolean().default(false),
    tags: z.array(z.string()).default([]),
    // Ordering + visibility
    order: z.number().default(99),
    draft: z.boolean().default(false),
    // Status shows honestly where the project stands.
    status: z.enum(['live', 'in-progress', 'concept', 'shipped']).default('shipped'),
    // Optional per-project accent (CSS color) for subtle theming.
    accent: z.string().optional(),
    // External links surfaced in the header.
    // url may be absolute (https://…) or a site-relative path (/assets/…).
    links: z
      .array(z.object({ label: z.string(), url: z.string() }))
      .default([]),
    // Cover image path under /public (e.g. /assets/bhchp/cover.png). Used by
    // the homepage project card only — the case-study page itself always
    // shows placeholder image slots (see CaseStudyLayout).
    cover: z.string().optional(),
    coverAlt: z.string().optional(),
    // Embeddable slide/deck URL (e.g. a Canva "view?embed" link) shown in the
    // case-study hero in place of the placeholder image box.
    heroEmbed: z.string().optional(),
    // Video (e.g. an .mp4 under /public) shown muted/looping in the hero in
    // place of the placeholder image or heroEmbed. Takes priority over both.
    heroVideo: z.string().optional(),
    // Opt into the pared-down section layout from the Figma "case-study-page"
    // frame (node 2018:3): no per-section description line, no challenge
    // pull-quote, no insight-card number/tag row, no solution features grid,
    // no impact comparison table. Same tokens/spacing everywhere else — see
    // CaseStudyLayout's `minimal` prop.
    minimal: z.boolean().default(false),

    // ------------------------------------------------------------------
    // Case-study page sections, rendered by src/layouts/CaseStudyLayout.astro
    // (numbered-section frame: Challenge → Insights → Process → Solution →
    // Impact → Reflection). Every string here is meant to hold placeholder
    // guidance until you write the real content — see any *.mdx file for
    // the current placeholder copy and shape to follow.
    // ------------------------------------------------------------------
    challengeDescription: z.string().optional(),
    challengeLead: z.string().optional(),
    challengeBody: z.string().optional(),
    quote: z.string().optional(),
    quoteAttribution: z.string().optional(),

    insightsDescription: z.string().optional(),
    insights: z
      .array(z.object({ tag: z.string(), title: z.string(), body: z.string() }))
      .default([]),

    processDescription: z.string().optional(),
    processIntro: z.string().optional(),
    // Optional embed (e.g. a slide deck PDF under /public) shown beside the
    // process write-up. When set, CaseStudyLayout widens that section's
    // sidebar column to make it legible — see CaseStudyLayout's
    // `processEmbed` prop.
    processEmbed: z.string().optional(),
    iterations: z
      .array(
        z.object({
          title: z.string(),
          caption: z.string(),
          // Real screenshot/photo under /public. Falls back to the layout's
          // dashed placeholder box when omitted.
          image: z.string().optional(),
          imageAlt: z.string().optional(),
        }),
      )
      .default([]),
    // Force the full-width, alternating-row "showcase" process layout (see
    // CaseStudyLayout) even before real screenshots exist — iterations
    // without an `image` render a blank placeholder box at showcase size.
    processShowcase: z.boolean().default(false),

    // Drop the Solution section entirely and renumber the sections after it
    // up, without deleting the fields below — see CaseStudyLayout's
    // `hideSolution` prop.
    hideSolution: z.boolean().default(false),
    solutionDescription: z.string().optional(),
    // Interactive Figma prototype shown in place of the solution mockup
    // placeholder — see CaseStudyLayout's `solutionEmbed`/`solutionEmbedTitle`.
    solutionEmbed: z.string().optional(),
    solutionEmbedTitle: z.string().optional(),
    solutionEmbedCaption: z.string().optional(),
    // Muted, looping demo video shown in place of the mockup placeholder —
    // see CaseStudyLayout's `solutionVideo` prop (takes priority over
    // solutionEmbed).
    solutionVideo: z.string().optional(),
    // Skip the generic mockup/overlay placeholder block entirely — use when
    // `solutionShowcase` already carries the section's real visuals. See
    // CaseStudyLayout's `hideSolutionMock` prop.
    hideSolutionMock: z.boolean().default(false),
    overlayTag: z.string().optional(),
    overlayTitle: z.string().optional(),
    overlayBody: z.string().optional(),
    features: z
      .array(z.object({ title: z.string(), body: z.string() }))
      .default([]),
    // Additional full-width, alternating-row sub-sections within Solution
    // (e.g. "the dashboard's hover state," "the poster in a real bus
    // shelter") — same shape as `iterations`, rendered the same way.
    solutionShowcase: z
      .array(
        z.object({
          title: z.string(),
          caption: z.string(),
          image: z.string().optional(),
          imageAlt: z.string().optional(),
          // Alternative to `image`: multiple separate photos shown as a
          // loose, mismatched-size collage (not flattened into one file) —
          // see CaseStudyLayout's `.cs2-showcase__collage`.
          images: z
            .array(z.object({ src: z.string(), alt: z.string().optional() }))
            .optional(),
        }),
      )
      .default([]),

    // Drop the Impact & Results section entirely and renumber the sections
    // after it up, without deleting the fields below — see CaseStudyLayout's
    // `hideImpact` prop.
    hideImpact: z.boolean().default(false),
    impactDescription: z.string().optional(),
    kpis: z
      .array(z.object({ value: z.string(), label: z.string(), body: z.string() }))
      .default([]),
    tableTitle: z.string().optional(),
    tableRows: z
      .array(z.object({ metric: z.string(), before: z.string(), after: z.string() }))
      .default([]),

    reflectionDescription: z.string().optional(),
    reflectionLead: z.string().optional(),
    reflectionBody: z.string().optional(),
  }),
});

export const collections = { work };
