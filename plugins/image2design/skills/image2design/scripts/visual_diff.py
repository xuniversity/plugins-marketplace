#!/usr/bin/env python3
"""Compare a reference image with a rendered screenshot for visual recreation work."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

try:
    from PIL import Image, ImageChops
except ImportError as exc:  # pragma: no cover - exercised only in missing envs
    raise SystemExit("Pillow is required: python -m pip install pillow") from exc


def parse_hex_color(value: str) -> tuple[int, int, int]:
    raw = value.strip().lstrip("#")
    if len(raw) != 6:
        raise argparse.ArgumentTypeError("background must be a 6-digit hex color")
    try:
        return tuple(int(raw[i : i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]
    except ValueError as exc:
        raise argparse.ArgumentTypeError("background must be a valid hex color") from exc


def load_rgb(path: Path, background: tuple[int, int, int]) -> Image.Image:
    image = Image.open(path).convert("RGBA")
    base = Image.new("RGBA", image.size, (*background, 255))
    return Image.alpha_composite(base, image).convert("RGB")


def pct_over(histogram: list[int], total: int, threshold: int) -> float:
    return round(sum(histogram[threshold + 1 :]) * 100 / total, 4)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare a reference image with a rendered screenshot and optionally write a red diff overlay."
    )
    parser.add_argument("reference", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--out", type=Path, help="write a red overlay diff image")
    parser.add_argument(
        "--background",
        type=parse_hex_color,
        default=(255, 255, 255),
        help="hex background used to flatten transparency, default #ffffff",
    )
    parser.add_argument(
        "--resize-candidate",
        action="store_true",
        help="resize candidate to reference size before comparing",
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=32,
        help="delta threshold used for changed_bbox and visible pixel percentage",
    )
    parser.add_argument("--fail-mean", type=float, help="exit 1 if mean_abs_delta exceeds this value")
    parser.add_argument(
        "--fail-pct-over-threshold",
        type=float,
        help="exit 1 if percent of pixels over --threshold exceeds this value",
    )
    args = parser.parse_args()

    if not args.reference.exists():
        raise SystemExit(f"reference does not exist: {args.reference}")
    if not args.candidate.exists():
        raise SystemExit(f"candidate does not exist: {args.candidate}")
    if not 0 <= args.threshold <= 255:
        raise SystemExit("--threshold must be between 0 and 255")

    reference = load_rgb(args.reference, args.background)
    candidate = load_rgb(args.candidate, args.background)

    resized_candidate = False
    if reference.size != candidate.size:
        if not args.resize_candidate:
            result = {
                "ok": False,
                "error": "size_mismatch",
                "reference_size": list(reference.size),
                "candidate_size": list(candidate.size),
                "hint": "capture the same viewport or pass --resize-candidate for an approximate comparison",
            }
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return 2
        candidate = candidate.resize(reference.size, Image.Resampling.LANCZOS)
        resized_candidate = True

    diff = ImageChops.difference(reference, candidate)
    gray = diff.convert("L")
    histogram = gray.histogram()
    total = reference.size[0] * reference.size[1]
    mean_abs_delta = sum(value * count for value, count in enumerate(histogram)) / total
    rms_delta = math.sqrt(sum((value * value) * count for value, count in enumerate(histogram)) / total)
    threshold_mask = gray.point(lambda value: 255 if value > args.threshold else 0)
    changed_bbox = threshold_mask.getbbox()
    pct_over_threshold = pct_over(histogram, total, args.threshold)

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        alpha = gray.point(lambda value: min(220, value * 4))
        overlay = Image.new("RGBA", reference.size, (255, 0, 0, 0))
        overlay.putalpha(alpha)
        base = candidate.convert("RGBA")
        Image.alpha_composite(base, overlay).save(args.out)

    result = {
        "ok": True,
        "reference_size": list(reference.size),
        "candidate_size": list(candidate.size),
        "resized_candidate": resized_candidate,
        "mean_abs_delta": round(mean_abs_delta, 4),
        "rms_delta": round(rms_delta, 4),
        "pct_pixels_over_8": pct_over(histogram, total, 8),
        "pct_pixels_over_16": pct_over(histogram, total, 16),
        "pct_pixels_over_32": pct_over(histogram, total, 32),
        "pct_pixels_over_64": pct_over(histogram, total, 64),
        "threshold": args.threshold,
        "pct_pixels_over_threshold": pct_over_threshold,
        "changed_bbox": list(changed_bbox) if changed_bbox else None,
        "diff_overlay": str(args.out) if args.out else None,
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))

    failed = False
    if args.fail_mean is not None and mean_abs_delta > args.fail_mean:
        failed = True
    if args.fail_pct_over_threshold is not None and pct_over_threshold > args.fail_pct_over_threshold:
        failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
