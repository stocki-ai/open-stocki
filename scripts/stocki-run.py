#!/usr/bin/env python3
"""
Submit Stocki quant analysis.

Usage:
    python3 stocki-run.py submit <question> [--task-id TASK_ID] [--timezone Asia/Shanghai]

Stdout: task info
Stderr: error messages
Exit:   0 success, 1 auth/client error, 2 service error, 3 rate limited/quota
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _gateway import gateway_request


def cmd_submit(args):
    body = {"question": args.question, "timezone": args.timezone}
    if args.task_id:
        body["task_id"] = args.task_id

    result = gateway_request("POST", "/v1/quant", body, timeout=30)
    print(f"task_id: {result.get('task_id', '')}")
    print(f"task_name: {result.get('task_name', '')}")


def main():
    parser = argparse.ArgumentParser(description="Submit Stocki quant analysis.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_submit = sub.add_parser("submit", help="Submit a quant analysis")
    p_submit.add_argument("question", help="Analysis question")
    p_submit.add_argument("--task-id", default=None, help="Existing task ID for iteration")
    p_submit.add_argument("--timezone", default="Asia/Shanghai", help="IANA timezone (default: Asia/Shanghai)")

    args = parser.parse_args()
    {"submit": cmd_submit}[args.command](args)


if __name__ == "__main__":
    main()
