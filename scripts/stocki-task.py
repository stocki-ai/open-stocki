#!/usr/bin/env python3
"""
List and inspect Stocki quant tasks.

Usage:
    python3 stocki-task.py list
    python3 stocki-task.py status <task_id>

Stdout: task info
Stderr: error messages
Exit:   0 success, 1 auth/client error, 2 service error, 3 rate limited/quota
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _gateway import gateway_request


def cmd_list(_args):
    result = gateway_request("GET", "/v1/tasks", timeout=30)
    tasks = result.get("tasks", [])
    if not tasks:
        print("No tasks found.")
        return
    print(f"{'Name':<40} {'Task ID':<16} {'Updated':<24} {'Msgs':>4}")
    print("-" * 88)
    for t in tasks:
        name = t.get("name", "")[:38]
        tid = t.get("task_id", "")
        updated = t.get("updated_at", "")[:19]
        msgs = t.get("message_count", 0)
        print(f"{name:<40} {tid:<16} {updated:<24} {msgs:>4}")


def cmd_status(args):
    result = gateway_request("GET", f"/v1/tasks/{args.task_id}", timeout=120)
    name = result.get("name", "")
    print(f"Task: {name} ({args.task_id})")

    current = result.get("current_run")
    if current:
        print(f"\nCurrent run: {current.get('run_id', '')} [{current.get('status', '')}]")
        print(f"  Query: {current.get('query', '')}")

    runs = result.get("runs", [])
    if runs:
        print(f"\nRuns ({len(runs)}):")
        for r in runs:
            status = r.get("status", "")
            rid = r.get("run_id", "")
            query = r.get("query", "")[:60]
            summary = r.get("summary") or ""
            err = r.get("error_message") or ""
            print(f"  [{status}] {rid}: {query}")
            if summary:
                print(f"    Summary: {summary[:120]}")
            if err:
                print(f"    Error: {err}")
            files = r.get("files", [])
            if files:
                print(f"    Files: {', '.join(files)}")


def main():
    parser = argparse.ArgumentParser(description="List and inspect Stocki quant tasks.")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="List all tasks")

    p_status = sub.add_parser("status", help="Show task details and run status")
    p_status.add_argument("task_id", help="Task ID")

    args = parser.parse_args()
    {"list": cmd_list, "status": cmd_status}[args.command](args)


if __name__ == "__main__":
    main()
