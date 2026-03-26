#!/usr/bin/env python3
"""
Download Stocki task result files (reports, charts).

Usage:
    python3 stocki-report.py list <task_id>
    python3 stocki-report.py download <task_id> <file_path> [--output local_path]

Stdout: file list or save confirmation
Stderr: error messages
Exit:   0 success, 1 auth/client error, 2 service error, 3 rate limited/quota
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _gateway import gateway_request, gateway_request_raw


def cmd_list(args):
    result = gateway_request("GET", f"/v1/tasks/{args.task_id}", timeout=120)
    runs = result.get("runs", [])
    if not runs:
        print("No runs found.")
        return
    for r in runs:
        rid = r.get("run_id", "")
        status = r.get("status", "")
        files = r.get("files", [])
        if files:
            print(f"[{status}] {rid}:")
            for f in files:
                print(f"  {f}")
        else:
            print(f"[{status}] {rid}: (no files)")


def cmd_download(args):
    raw, content_type = gateway_request_raw(
        "GET",
        f"/v1/tasks/{args.task_id}/files/{args.file_path}",
        timeout=300,
    )
    output = args.output or os.path.basename(args.file_path)

    mode = "wb" if "image" in content_type else "w"
    with open(output, mode) as f:
        if mode == "wb":
            f.write(raw)
        else:
            f.write(raw.decode("utf-8"))
    print(f"Saved: {output} ({len(raw)} bytes)")


def main():
    parser = argparse.ArgumentParser(description="Download Stocki task result files.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list", help="List files for a task")
    p_list.add_argument("task_id", help="Task ID")

    p_dl = sub.add_parser("download", help="Download a file")
    p_dl.add_argument("task_id", help="Task ID")
    p_dl.add_argument("file_path", help="File path (e.g. runs/run_001/report.md)")
    p_dl.add_argument("--output", help="Local output path (default: basename of file_path)")

    args = parser.parse_args()
    {"list": cmd_list, "download": cmd_download}[args.command](args)


if __name__ == "__main__":
    main()
