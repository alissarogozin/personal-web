// @ts-check
import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';

// https://astro.build/config
export default defineConfig({
  // Host-agnostic static output. When you pick a host, set `site` (and `base`
  // if deploying to a GitHub Pages project subpath, e.g. user.github.io/repo).
  // site: 'https://your-domain.com',
  integrations: [mdx()],
});
