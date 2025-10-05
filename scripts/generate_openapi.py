#!/usr/bin/env python3
"""Generate the OpenAPI schema for the Image Store Service."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from fastapi.openapi.utils import get_openapi

from iss import app


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate OpenAPI schema JSON")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("dist/openapi.json"),
        help="Where to write the OpenAPI document (default: dist/openapi.json)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    schema = get_openapi(
        title=app.title,
        version="1.0.0",
        routes=app.routes,
        description=app.description,
    )
    with args.output.open("w", encoding="utf-8") as fp:
        json.dump(schema, fp, indent=2, sort_keys=True)
        fp.write("\n")


if __name__ == "__main__":
    main()
