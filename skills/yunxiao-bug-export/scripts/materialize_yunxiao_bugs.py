#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

from harvest_common import materialize_run


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--list-url", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--list-cache-file", required=True)
    parser.add_argument("--full-json-file", required=True)
    parser.add_argument("--run-date")
    parser.add_argument(
        "--image-map-file",
        help="Optional JSON map keyed by remote image URL with localPath/fileId fields.",
    )
    parser.add_argument(
        "--source",
        default="yunxiao-mcp",
        help="Source label written to run-meta.json. Default: yunxiao-mcp",
    )
    return parser.parse_args()


def load_json(path: str):
    return json.loads(Path(path).read_text())


def main():
    args = parse_args()
    list_data = load_json(args.list_cache_file)
    full_items = load_json(args.full_json_file)
    image_map = load_json(args.image_map_file) if args.image_map_file else None

    result = materialize_run(
        output_dir=args.output_dir,
        run_date=args.run_date,
        list_url=args.list_url,
        list_data=list_data,
        full_items=full_items,
        image_map=image_map,
        source=args.source,
    )

    paths = result["paths"]
    print("Materialization complete:")
    print(f"  run dir:    {paths['run_dir']}")
    print(f"  readme:     {paths['readme_md']}")
    print(f"  list cache: {paths['list_cache']}")
    print(f"  full json:  {paths['full_json']}")
    print(f"  summary:    {paths['summary_json']}")
    print(f"  grouped md: {paths['grouped_md']}")
    print(f"  count:      {len(result['summary_items'])}")


if __name__ == "__main__":
    main()
