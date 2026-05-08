#!/usr/bin/env python3
"""UAASP Skill Usage Tracker

Logs skill usage metrics to tracking/metrics.jsonl.

Usage:
    python3 scripts/track.py --skill <name> --tool <tool> --success <true|false> --duration <ms>
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone


def main():
    parser = argparse.ArgumentParser(description="Track UAASP skill usage")
    parser.add_argument("--skill", required=True, help="Skill name (e.g., autoplan)")
    parser.add_argument("--tool", required=True, choices=["claude", "opencode", "codex", "pi"],
                        help="AI tool that used the skill")
    parser.add_argument("--success", required=True, choices=["true", "false"],
                        help="Whether the skill execution succeeded")
    parser.add_argument("--duration", required=True, type=int,
                        help="Execution duration in milliseconds")

    args = parser.parse_args()

    # Build metrics record
    record = {
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "skill_name": args.skill,
        "tool": args.tool,
        "success": args.success == "true",
        "duration_ms": args.duration
    }

    # Determine metrics file path (relative to project root)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    metrics_path = os.path.join(project_root, "tracking", "metrics.jsonl")

    # Ensure tracking directory exists
    os.makedirs(os.path.dirname(metrics_path), exist_ok=True)

    # Append to JSONL file
    with open(metrics_path, "a") as f:
        f.write(json.dumps(record) + "\n")

    print(f"Logged: {args.skill} via {args.tool} ({'success' if record['success'] else 'failure'}) in {args.duration}ms")
    print(f"Metrics file: {metrics_path}")


if __name__ == "__main__":
    main()
