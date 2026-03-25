#!/usr/bin/env python3
"""
List and download Stocki analysis reports.

Usage:
    python3 stocki-report.py list <task_id>
    python3 stocki-report.py download <task_id> <filename> [--output path.md]

Stdout: report list or content
Stderr: error messages
Exit:   0 success, 1 auth/client error, 2 service error
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _gateway import gateway_request


def cmd_list(args):
    result = gateway_request("GET", f"/v1/tasks/{args.task_id}/reports", timeout=300)
    reports = result.get("reports", [])
    if not reports:
        print("No reports found.")
        return
    print(f"{'Filename':<40} {'Size':>10} {'Created':<24}")
    print("-" * 76)
    for r in reports:
        name = r.get("filename", "")
        size = r.get("size_bytes", 0)
        created = r.get("created_at", "")[:19]
        print(f"{name:<40} {size:>10} {created:<24}")


def cmd_download(args):
    result = gateway_request(
        "GET",
        f"/v1/tasks/{args.task_id}/reports/{args.filename}",
        timeout=300,
    )
    content = result.get("content", "")
    output = args.output or args.filename

    with open(output, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Saved: {output} ({len(content)} bytes)")


def main():
    parser = argparse.ArgumentParser(description="List and download Stocki reports.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list", help="List reports for a task")
    p_list.add_argument("task_id", help="Task ID (UUID)")

    p_dl = sub.add_parser("download", help="Download a report")
    p_dl.add_argument("task_id", help="Task ID (UUID)")
    p_dl.add_argument("filename", help="Report filename")
    p_dl.add_argument("--output", help="Output file path (default: same as filename)")

    args = parser.parse_args()
    {"list": cmd_list, "download": cmd_download}[args.command](args)


if __name__ == "__main__":
    main()
