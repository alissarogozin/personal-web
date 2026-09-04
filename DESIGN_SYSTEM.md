# Personal Site — Design System

**Direction:** Black & cream editorial, magazine-style. Simple, warm, human. Color used sparingly, as a highlight — not a theme.

---

## 1. Color

```css
:root {
  /* Base */
  --color-bg:          #F7F4EC;  /* warm cream, not pure white */
  --color-bg-alt:      #EFEAE0;  /* deeper cream, for cards/panels */
  --color-ink:         #1B1815;  /* near-black, warm not blue-black */
  --color-ink-soft:    #4A453F;  /* body text, softer than headline black */
  --color-line:        #DDD6C7;  /* hairline borders, dividers */

  /* Accent */
  --color-accent-rust:    #B5502E; /* warm terracotta */
  --color-accent-magenta: #C23B6B; /* scrawl-pink pop */

  /* Utility */
  --color-white:   #FFFFFF;
  --color-overlay: rgba(27, 24, 21, 0.6);
}
```

**Usage rule:** the page should read fine in grayscale. Accent color shows up on one nav element, link hovers, tags/pills, or a single emphasized word — never as a large background fill.

---

## 2. Typography

**Font pairing:** Montserrat (structural, geometric sans) for headlines, nav, and labels + Lora (warm serif) for body copy, so long paragraphs stay easy to read against Montserrat's cleaner edges. Petit Formal Script is the signature accent — used once per page, never for running text.

```css
:root {
  --font-display: "Montserrat", "Helvetica Neue", Arial, sans-serif;
  --font-body:    "Lora", Georgia, serif;
  --font-accent:  "Petit Formal Script", cursive; /* one use per page, max */
}
```

### Type hierarchy

| Level | Font | Size | Weight | Line-height | Use |
|---|---|---|---|---|---|
| Hero | Montserrat | `clamp(2.5rem, 6vw, 4.5rem)` | 600 | 1.1 | Page-level headline |
| H1 | Montserrat | `clamp(2rem, 4vw, 3rem)` | 600 | 1.15 | Section titles |
| H2 | Montserrat | 1.75rem | 500 | 1.2 | Sub-section titles |
| H3 | Montserrat | 1.25rem | 500 | 1.3 | Card/block titles |
| Body | Lora | 1.0625rem | 400 | 1.7 | Paragraph copy |
| Small | Lora | 0.875rem | 400 | 1.6 | Captions, meta text |
| Label | Montserrat | 0.75rem | 500 | 1.0 | Nav items, eyebrow tags — uppercase, letter-spaced |
| Accent | Petit Formal Script | 1.75–2.5rem | 400 | 1.0 | One signature word per page |

```css
:root {
  --fs-hero:  clamp(2.5rem, 6vw, 4.5rem);
  --fs-h1:    clamp(2rem, 4vw, 3rem);
  --fs-h2:    1.75rem;
  --fs-h3:    1.25rem;
  --fs-body:  1.0625rem;
  --fs-small: 0.875rem;
  --fs-label: 0.75rem;
  --fs-accent: 2rem;

  --fw-regular: 400;
  --fw-medium:  500;
  --fw-semibold: 600;

  --lh-tight: 1.15;
  --lh-body:  1.7;

  --tracking-label: 0.08em;
}
```

**Rule of thumb:** never more than one Montserrat weight and one Lora weight per screen — 600 for headlines, 400 for everything else, keeps the hierarchy from getting muddy.

---

## 3. Spacing

```css
:root {
  --space-xs:  0.5rem;   /* 8px  — tight internal gaps */
  --space-sm:  1rem;     /* 16px — related elements */
  --space-md:  1.5rem;   /* 24px — paragraph-to-paragraph */
  --space-lg:  2.5rem;   /* 40px — block-to-block */
  --space-xl:  4rem;     /* 64px — component-to-component */
  --space-2xl: 6rem;     /* 96px — sub-section breaks */
  --space-3xl: 9rem;     /* 144px — major page section breaks */

  --content-max: 1200px;
  --text-max:    640px;  /* body copy column width, for readability */
  --page-gutter: clamp(1.5rem, 6vw, 6rem);

  --gap-grid: 2rem;      /* default gap in card/image grids */
}
```

**Spacing rule:** section breaks (`--space-3xl`) should feel generous enough to read as a deliberate pause — that's what makes cream space feel editorial instead of just empty. Inside a text block, keep spacing tight (`--space-md`) so paragraphs read as one continuous thought.

### Padding

Padding is deliberately narrower than the margin/spacing scale — components should feel tight and considered on the inside, even when the page around them feels generous.

```css
:root {
  --pad-button-y: 0.625rem;  /* 10px — pill buttons, vertical */
  --pad-button-x: 1.5rem;    /* 24px — pill buttons, horizontal */
  --pad-tag:      0.375rem 0.875rem; /* 6px / 14px — small pills, tags */
  --pad-card:     2.5rem;    /* 40px — cards, panels (all sides) */
  --pad-card-sm:  1.5rem;    /* 24px — compact cards, mobile cards */
  --pad-input:    0.75rem 1rem; /* 12px / 16px — form fields */
  --pad-section:  var(--page-gutter) 0; /* section vertical padding uses page gutter */
}
```

**Padding rule:** buttons and tags use fixed rem values (they shouldn't grow with viewport). Cards use `--pad-card` on desktop and drop to `--pad-card-sm` below ~640px — content should never feel cramped against a card edge, but padding shouldn't scale up so much it swallows small components.

---

## 4. Components

- **Nav:** Montserrat wordmark left, uppercase Montserrat label links right, one pill-style CTA button (outline default, filled on hover).
- **Cards:** `--color-bg-alt` background, 12–16px radius, padding ≥ `--space-lg`.
- **Buttons:** pill-shaped, outline by default, accent fill only on hover/active.
- **Tags/labels:** small pill or plain uppercase Montserrat label in accent color — safest surface for a color "pop."
- **Dividers:** thin hairline (`--color-line`), never a heavy rule.
- **Accent moments:** the script font appears once per page — a single word inside a headline, or a small eyebrow tag — never in body copy or nav.

---

### For Claude Code

Define these as CSS variables (or Tailwind theme extension) at the project root, then build components referencing only the variables — no hardcoded hex/px values inside components.
