#!/usr/bin/env python3
"""Generate a basic SLSA provenance predicate for the built container image."""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate provenance predicate")
    parser.add_argument("--image", required=True, help="Image name, e.g. ghcr.io/org/repo")
    parser.add_argument("--digest", required=True, help="Image digest, e.g. sha256:deadbeef")
    parser.add_argument("--version", required=True, help="Version tag, e.g. v1.0.0")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("dist/provenance.json"),
        help="Output file for the provenance predicate",
    )
    return parser.parse_args()


def iso_now() -> str:
    return datetime.now(tz=timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def main() -> None:
    args = parse_args()
    digest_value = args.digest.split(":", 1)[-1]
    repo = os.getenv("GITHUB_REPOSITORY", "")
    source_ref = os.getenv("GITHUB_REF", "")
    commit_sha = os.getenv("GITHUB_SHA", "")
    server_url = os.getenv("GITHUB_SERVER_URL", "https://github.com")
    source_uri = f"git+{server_url}/{repo}@{commit_sha}"

    started = iso_now()
    statement = {
        "_type": "https://in-toto.io/Statement/v1",
        "subject": [
            {
                "name": args.image,
                "digest": {"sha256": digest_value},
            }
        ],
        "predicateType": "https://slsa.dev/provenance/v1",
        "predicate": {
            "buildDefinition": {
                "buildType": "https://github.com/Attestations/GitHubActionsWorkflow@v1",
                "externalParameters": {
                    "source": source_uri,
                    "workflow": os.getenv("GITHUB_WORKFLOW", ""),
                    "workflow_ref": source_ref,
                    "version": args.version,
                },
                "internalParameters": {},
                "resolvedDependencies": [],
            },
            "runDetails": {
                "builder": {
                    "id": "https://github.com/actions/runner",
                },
                "metadata": {
                    "invocationId": os.getenv("GITHUB_RUN_ID", ""),
                    "startedOn": started,
                    "finishedOn": iso_now(),
                },
            },
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(statement, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
