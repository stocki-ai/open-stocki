#!/usr/bin/env python3
"""
Submit and check Stocki quant runs.

Usage:
    python3 stocki-run.py submit <task_id> <query> [--timezone Asia/Shanghai]
    python3 stocki-run.py status <task_id> <run_id>

Stdout: run info / status
Stderr: error messages
Exit:   0 success, 1 auth/client error, 2 service error
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _gateway import format_for_wechat, gateway_request


def cmd_submit(args):
    result = gateway_request(
        "POST",
        f"/v1/tasks/{args.task_id}/runs",
        {"query": args.query, "timezone": args.timezone},
        timeout=30,
    )
    print(f"run_id: {result.get('run_id', '')}")
    print(f"status: {result.get('status', '')}")
    pos = result.get("queue_position")
    if pos is not None:
        print(f"queue_position: {pos}")


def cmd_status(args):
    result = gateway_request(
        "GET",
        f"/v1/tasks/{args.task_id}/runs/{args.run_id}",
        timeout=120,
    )
    status = result.get("status", "unknown")
    print(f"status: {status}")

    if status == "queued":
        pos = result.get("queue_position")
        if pos is not None:
            print(f"queue_position: {pos}")
    elif status == "error":
        msg = result.get("message", "Unknown error")
        print(f"error: {msg}", file=sys.stderr)
        sys.exit(1)
    elif status == "success":
        answer = result.get("answer", "")
        if answer:
            print()
            print(format_for_wechat(answer))


def main():
    parser = argparse.ArgumentParser(description="Submit and check Stocki quant runs.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_submit = sub.add_parser("submit", help="Submit a quant run")
    p_submit.add_argument("task_id", help="Task ID (UUID)")
    p_submit.add_argument("query", help="Analysis query")
    p_submit.add_argument("--timezone", default="Asia/Shanghai", help="IANA timezone (default: Asia/Shanghai)")

    p_status = sub.add_parser("status", help="Check run status")
    p_status.add_argument("task_id", help="Task ID (UUID)")
    p_status.add_argument("run_id", help="Run ID")

    args = parser.parse_args()
    {"submit": cmd_submit, "status": cmd_status}[args.command](args)


if __name__ == "__main__":
    main()
