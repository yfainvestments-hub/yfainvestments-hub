---
name: awesome-design-md
description: A decoded design-system reference library ("design.md") for 70+ real-world brands (Apple, Stripe, Linear, Notion, Figma, Vercel, Airbnb, Tesla, and more). Use when the user wants a website, app, or component to adopt the look-and-feel of a specific well-known brand, or asks for a concrete palette / typography / spacing / component vocabulary to build in. Steal the design blocks, not the site.
license: See UPSTREAM_README.md (VoltAgent/awesome-design-md)
---

# awesome-design-md — brand design systems, decoded

A curated library of `design.md` files that capture how real, well-known products
look: color palettes, typography, spacing scale, radii, shadows, and component
patterns — written as agent-friendly Markdown you can build against directly.

Source: VoltAgent/awesome-design-md. This skill vendors the `design-md/` library
and adds this entry point. It is **reference material**, not a build tool — pair it
with a frontend/taste skill (e.g. `design-taste-frontend`, `impeccable`) to ship.

## When to use

- The user names a brand or vibe: "make it feel like Linear", "Stripe-style
  landing page", "Notion-clean dashboard", "Apple product page".
- You need a concrete, opinionated palette / type / spacing system to anchor a
  design instead of inventing generic defaults (the "AI slop" failure mode).
- The user wants to compare how several brands solve the same UI problem.

## How to use

1. **Pick the closest brand** to the requested vibe from `design-md/` (74 available;
   see the list below). If none fits, choose the nearest one or two and blend.
2. **Read that brand's file**, e.g. `design-md/linear.app/` — pull the palette,
   type scale, spacing, radii, and component notes.
3. **Extract the system, not the pixels.** Adapt tokens to the user's content and
   brand; do not clone the source site's copy, logos, or proprietary assets.
4. **Hand the tokens to a build skill** to generate the actual UI.

## Available brands

airbnb, airtable, apple, binance, bmw, bmw-m, bugatti, cal, claude, clay,
clickhouse, cohere, coinbase, composio, cursor, dell-1996, elevenlabs, expo,
ferrari, figma, framer, hashicorp, hp, ibm, intercom, kraken, lamborghini,
linear.app, lovable, mastercard, meta, minimax, mintlify, miro, mistral.ai,
mongodb, nike, nintendo-2001, notion, nvidia, ollama, opencode.ai, pinterest,
playstation, posthog, raycast, renault, replicate, resend, revolut, runwayml,
sanity, sentry, shopify, slack, spacex, spotify, starbucks, stripe, supabase,
superhuman, tesla, theverge, together.ai, uber, vercel, vodafone, voltagent,
warp, webflow, wired, wise, x.ai, zapier.

## Guardrails

- These files describe **third-party brands**. Use them as inspiration and to
  match a requested aesthetic — never to impersonate a brand, reproduce its
  logo/wordmark, or pass work off as coming from that company.
- When a user's own brand exists, prefer their tokens; use these as a starting
  scaffold only.
