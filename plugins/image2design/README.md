# image2design

Codex plugin for turning screenshots, UI mockups, generated design images, posters, and other raster references into high-fidelity responsive design implementations.

The plugin installs the `$image2design` skill. It is Codex-oriented because the workflow depends on Codex image generation (`$imagegen`), local browser screenshots, and visual diff overlays.

Core workflow:

- inspect the reference image and define fidelity targets
- generate bitmap assets for complex badges, medals, textures, stickers, or pictorial UI art
- implement a responsive design instead of locking to the reference screenshot size
- capture a browser screenshot at the reference viewport
- run `visual_diff.py` and inspect the diff overlay
- iterate on proportions, spacing, color, typography, shadows, and asset quality
- verify one additional non-reference viewport for responsive UI
