---
name: image2design
description: Convert a screenshot, generated design image, UI mockup, poster, landing-page comp, or other raster reference into a high-fidelity responsive design implementation. Use when Codex is asked to recreate an image as frontend code or a design draft, match a visual reference closely, generate project-bound bitmap assets via $imagegen, and iteratively refine with browser screenshots plus visual diff overlays.
---

# Image2Design

## Overview

Recreate raster design references as high-fidelity responsive design implementations with a measurable visual-matching loop. The workflow emphasizes visual inventory, dependent asset generation or extraction, browser screenshot verification, and targeted refinement instead of a one-pass approximate implementation.

## Core Contract

Always optimize for visual fidelity to the supplied image. Do not simplify difficult areas into generic cards, gradients, placeholder blocks, or approximate icons when the reference contains specific texture, illustration, imagery, spacing, typography, or lighting details.

Treat complex pictorial UI elements as raster assets, not code exercises. If the reference contains ornate badges, medals, stickers, product-like icons, textured illustrations, decorative objects, or any small graphic whose fidelity would be poor in CSS/SVG, proactively use `$imagegen` to create a bitmap dependency and place the selected asset inside the workspace before referencing it.

Produce or update real project files. Prefer a standalone HTML file with Tailwind CDN only when the user asks for a portable artifact or the repo has no frontend build system. Inside an existing project, follow the local framework, styling system, asset conventions, and dev-server workflow.

Reference dimensions are a calibration target, not automatically the final product dimensions. Use the source image's width and height to take like-for-like screenshots and run visual diff, but build the deliverable with responsive constraints unless the user explicitly asks for a fixed-size poster, export, or pixel-locked artifact.

## Workflow

1. Confirm the target output: standalone responsive design draft, frontend implementation in the current app, or another project-appropriate artifact. If the user did not specify and there is no obvious project target, create a portable `index.html` next to the supplied image or in a clearly named output folder.
2. Inspect the reference image before coding. Record dimensions, aspect ratio, major regions, background treatment, typography, spacing rhythm, shadows, texture, icons, illustrations, photos, and any repeated motifs.
3. Decide the layout policy. Use the reference viewport for calibration screenshots. For ordinary web/app UI, build a responsive layout with `max-width`, grid/flex constraints, stable aspect ratios, and sensible breakpoints instead of hard-locking the page to the reference pixel size.
4. Build an asset plan. Classify each visual element as CSS-native, text, existing repo asset, extractable from the source image, or generated dependency. Mark ornate badges, medals, complex icons, stickers, textures, and pictorial decorations as `$imagegen` candidates by default.
5. Use `$imagegen` for dependent raster elements that are hard to code faithfully: textures, decorative illustrations, product-like objects, photo inserts, background plates, stickers, medals, badges, or complex icon art. Save project-bound generated assets inside the workspace; never reference `$CODEX_HOME/generated_images` directly.
6. Implement the first faithful pass. Use measured constraints, project-appropriate CSS utilities or styling primitives, real images/assets, and stable responsive sizing. Avoid broad redesigns and avoid using CSS/SVG stand-ins for generated-asset candidates unless `$imagegen` is unavailable or the user explicitly prefers code-native assets.
7. Render in a browser at the reference viewport. Take a like-for-like screenshot of the coded result.
8. Run `scripts/visual_diff.py` against the reference and coded screenshot. Use the metrics and diff overlay to identify the largest visual mismatches.
9. Iterate with targeted fixes: geometry and proportions first, then spacing, colors, typography, shadows, generated assets, texture, and small details. Re-screenshot after meaningful changes.
10. Render at least one non-reference viewport when the deliverable is a web/app UI, to verify the result did not become a fixed screenshot clone.
11. Finish only after the result visually matches the reference closely enough for the user's stated purpose, and report saved files, generated assets, screenshot evidence, diff metrics, responsive verification, and any remaining known deviations.

## Fidelity Checklist

Before the first implementation pass, write a short checklist from the actual reference:

- Canvas: reference width, height, aspect ratio, safe area, and intended viewport.
- Layout: major bounding boxes, alignment axes, overlap layers, and z-index relationships.
- Color: background, surface, accent, text, gradient stops, and transparency.
- Type: font family guess, size, weight, line-height, letter spacing, casing, and exact text.
- Shape: border radius, stroke widths, dividers, masks, clip paths, and shadows.
- Raster assets: photos, textures, generated objects, extracted cutouts, icons, and noise.
- Responsiveness: which dimensions are calibration-only, which containers should stretch, wrap, or collapse, and which fixed-format elements need stable aspect ratios.
- Motion: only if the user requests an interactive recreation; keep static fidelity first.

Use this checklist as the acceptance target. If a region is hard to implement exactly, create or generate an asset for that region instead of flattening it into generic CSS.

## Asset Generation With `$imagegen`

Use `$imagegen` when an image subcomponent determines the fidelity and is not practical to reproduce with CSS. Examples: paper grain, realistic object renders, background artwork, hand-drawn ornaments, 3D shapes, scene fragments, sticker-like decorations, ornate achievement badges, medals, enamel pins, or complex pictorial icons.

For dashboard or enterprise UI screenshots, badge walls and award icons are a strong signal to use `$imagegen`. Prefer generating a sprite sheet or a small set of coordinated PNG/WebP assets, then use CSS background positioning or `<img>` placement in the implementation.

When prompting `$imagegen` for a dependent asset:

- State that the output is a component extracted from a larger UI recreation.
- Match the reference crop's perspective, lighting, texture, palette, and edge treatment.
- Request transparent or flat chroma-key background only when the asset must be layered over HTML.
- Avoid text unless the asset text is unavoidable; HTML text is usually more controllable.
- Save the final selected asset into the project and reference that path from the HTML/CSS.
- If the generated output is a sheet, crop or position it deliberately; do not leave rough prompt artifacts visible in the UI.

Good asset prompt pattern:

```text
Use case: ui-mockup
Asset type: dependent raster element for a high-fidelity responsive design recreation
Primary request: recreate only the <specific element> visible in the reference crop
Style/medium: match the supplied design image exactly
Composition/framing: centered object with generous padding for clean placement
Lighting/mood: match the source lighting and shadow softness
Color palette: match the source colors
Constraints: no text, no watermark, no background unless requested; keep edges clean for layering
```

## Implementation Guidance

- Prefer the project's styling system. For standalone artifacts, Tailwind utilities plus arbitrary values are a good default for exact spacing, dimensions, colors, shadows, and transforms.
- Use CSS variables for repeated measured values, colors, and shadows when they improve consistency.
- Use real `<img>` elements or CSS backgrounds for generated/extracted assets; preserve original aspect ratios.
- Use absolute positioning inside a fixed-aspect stage for image-like compositions, then wrap that stage responsively.
- Use semantic HTML only when it does not compromise visual fidelity; this skill is primarily for visual reconstruction.
- Use web fonts only when available or easy to load; otherwise choose the closest local/system fallback and note it.
- Do not replace specific visual content with generic lucide icons unless the reference actually uses simple line icons.
- Do not overfit to a single desktop size when the user expects responsive output. Keep the reference viewport exact, then define responsive behavior deliberately.
- Do not treat a reference screenshot size such as `1024x1536` as a mandate to create a fixed `1024px` by `1536px` page. Use that size for screenshot comparison; use responsive CSS for the deliverable unless fixed output is explicitly requested.

## Visual Diff Script

Use the bundled script after taking a browser screenshot:

```bash
python scripts/visual_diff.py \
  reference.png \
  rendered.png \
  --out diff-overlay.png
```

Read the JSON metrics:

- `mean_abs_delta`: overall difference; lower is better.
- `pct_pixels_over_32`: approximate share of visibly wrong pixels.
- `changed_bbox`: where the strongest mismatch is concentrated.
- `diff-overlay.png`: inspect visually to decide the next correction.

The script is a guide, not the only acceptance rule. Typography rendering, antialiasing, and generated assets can create harmless pixel differences; use the overlay to focus iteration on visible mismatches.

Calibration loop:

1. Capture a screenshot at the reference viewport.
2. Run `visual_diff.py` and inspect the red overlay.
3. Fix the largest visible mismatch in this order: layout proportions, spacing, colors, typography, shadows, raster asset quality.
4. Repeat after meaningful changes. Do not stop after one render for a non-trivial UI.
5. Capture a second screenshot at a non-reference viewport for responsive web/app deliverables.

## Completion Standard

Do not finish after the first render unless the reference is extremely simple. A completed response should include:

- The generated design implementation file path and any asset paths.
- The reference viewport used for screenshot verification.
- At least one non-reference viewport screenshot when the output is responsive UI.
- The visual diff command and key metrics, or a clear reason visual diff could not be run.
- Which dependent assets were generated with `$imagegen`, especially badges, medals, decorative icons, textures, or pictorial UI art.
- A concise list of remaining deviations if exact fidelity was limited by fonts, source resolution, missing assets, or user-provided constraints.
