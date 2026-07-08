# Design System: AMD Zero-Token Router

## 1. Visual Theme & Atmosphere
A cockpit-dense, cinematic dark mode interface designed for high-performance AI monitoring. The atmosphere feels like a premium, state-of-the-art telemetry dashboard—confident asymmetric layouts, hyper-legible mono-spaced typography for metrics, and fluid spring-physics motion for hover states. The visual tone is highly technical yet incredibly sleek, utilizing glassmorphism over a pitch-dark canvas to create profound depth without clutter. It balances a Density of 8 (Cockpit Dense) with a Motion rating of 6 (Fluid CSS) to feel alive but not distracting.

## 2. Color Palette & Roles
- **Abyss Canvas** (#0A0A0C) — Primary background surface. Pitch dark but not pure black.
- **Glass Surface** (rgba(24, 24, 27, 0.4)) — Card and container fill. Used with backdrop-blur for glassmorphism.
- **Titanium White** (#FAFAFA) — Primary text, critical data points, and active UI states.
- **Muted Steel** (#71717A) — Secondary text, descriptions, inactive states, and structural metadata.
- **Whisper Border** (rgba(255, 255, 255, 0.08)) — Card borders, 1px structural separator lines, and subtle input outlines.
- **AMD Crimson** (#EF0000) — Single accent color for critical active states, focus rings, and primary action buttons. Kept saturated but minimal in application to draw the eye without overwhelming.

## 3. Typography Rules
- **Display:** `Satoshi` — Track-tight, controlled scale, weight-driven hierarchy. Used for primary headers and section titles.
- **Body:** `Satoshi` — Relaxed leading, 65ch max-width, neutral secondary color. Highly legible for dense chat text.
- **Mono:** `JetBrains Mono` — For code blocks, routing metrics, timestamps, token counts, and all high-density numeric data.
- **Banned:** `Inter`, any generic system fonts (`Arial`, `Roboto`). Serif fonts (`Times New Roman`, `Georgia`, `Garamond`) are entirely banned for this premium software dashboard context.

## 4. Component Stylings
* **Buttons:** Flat, strictly geometric. Tactile push feedback via spring physics (`transform: scale(0.98)`) on active state. No neon outer glows. Accent fill for primary (AMD Crimson), ghostly translucent outline for secondary.
* **Cards:** Sharp, structural borders. Corners subtly rounded (0.5rem max). Used strictly to segment metric panels and chat bounds. Deep backdrop blur (`backdrop-blur-md`) with a Whisper Border to separate from the Abyss Canvas.
* **Inputs:** Minimalist command-line style. Label above, error below. Focus ring shifts border to AMD Crimson. No floating labels or overly tall input boxes.
* **Loaders:** Skeletal shimmer matching exact layout dimensions. No generic circular spinners.
* **Empty States:** Composed, structural terminal-like readouts indicating system readiness—not just a blank screen or a lazy "No data" text.

## 5. Layout Principles
Grid-first responsive architecture prioritizing CSS Grid over Flexbox math. Strict asymmetric splits for the dashboard—metrics and routing telemetry bound to a 300px fixed left sidebar, while the chat interface occupies the fluid remaining viewport. Strict single-column collapse below 768px (sidebar hides behind a clean mobile menu). No overlapping elements; every panel occupies its own clear spatial zone. Generous internal padding within cards but tight 1px gaps between structural panels.

## 6. Motion & Interaction
Spring physics for all interactive elements (default `stiffness: 100, damping: 20` for a premium, weighty feel). Perpetual micro-loops on active dashboard components (e.g., a subtle pulse on the active routing node: L1 vs L2). Staggered cascade reveals for loading historical chat messages. Animate exclusively via `transform` and `opacity` to ensure flawless 60fps performance. No linear easings.

## 7. Anti-Patterns (Banned)
- NEVER DO: Use emojis anywhere in the UI or copywriting.
- NEVER DO: Use `Inter` font or generic serifs.
- NEVER DO: Use pure black (`#000000`).
- NEVER DO: Add neon outer glows, extreme drop shadows, or oversaturated UI gradients.
- NEVER DO: Stack 3-column equal card layouts for features.
- NEVER DO: Use AI copywriting clichés like "Elevate", "Seamless", "Unleash", or "Next-Gen".
- NEVER DO: Include filler UI text like "Scroll to explore", bouncing chevrons, or scroll arrows.
- NEVER DO: Render fake round numbers (`99.99%`, `50%`) in the telemetry UI.
- NEVER DO: Use overlapping elements—clean spatial separation is mandatory.
