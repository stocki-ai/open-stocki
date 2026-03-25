#!/usr/bin/env python3
"""
Manage Stocki quant tasks.

Usage:
    python3 stocki-task.py create <name> [--description "..."]
    python3 stocki-task.py list
    python3 stocki-task.py history <task_id> [--page 1]

Stdout: task info
Stderr: error messages
Exit:   0 success, 1 auth/client error, 2 service error
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _gateway import gateway_request


def cmd_create(args):
    body = {"name": args.name}
    if args.description:
        body["description"] = args.description
    result = gateway_request("POST", "/v1/tasks", body, timeout=30)
    print(f"task_id: {result['task_id']}")
    print(f"name: {result['name']}")
    print(f"created_at: {result['created_at']}")


def cmd_list(_args):
    tasks = gateway_request("GET", "/v1/tasks", timeout=30)
    if not tasks:
        print("No tasks found.")
        return
    # Print as aligned table
    print(f"{'Name':<40} {'Task ID':<40} {'Updated':<24} {'Msgs':>4}")
    print("-" * 112)
    for t in tasks:
        name = t.get("name", "")[:38]
        tid = t.get("task_id", "")
        updated = t.get("updated_at", "")[:19]
        msgs = t.get("message_count", 0)
        print(f"{name:<40} {tid:<40} {updated:<24} {msgs:>4}")


def cmd_history(args):
    path = f"/v1/tasks/{args.task_id}"
    if args.page:
        path += f"?page={args.page}"
    result = gateway_request("GET", path, timeout=300)
    print(f"Task: {result.get('name', '')}  (page {result.get('page', 1)}/{result.get('total_pages', 1)})")
    print()
    for msg in result.get("messages", []):
        role = msg.get("role", "unknown").upper()
        ts = msg.get("timestamp", "")[:19]
        content = msg.get("content", "")
        print(f"[{role}] {ts}")
        print(content)
        print()


def main():
    parser = argparse.ArgumentParser(description="Manage Stocki quant tasks.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_create = sub.add_parser("create", help="Create a new task")
    p_create.add_argument("name", help="Task name (must be unique)")
    p_create.add_argument("--description", default="", help="Optional description")

    sub.add_parser("list", help="List all tasks")

    p_history = sub.add_parser("history", help="Show task conversation history")
    p_history.add_argument("task_id", help="Task ID (UUID)")
    p_history.add_argument("--page", type=int, default=1, help="Page number (default: 1)")

    args = parser.parse_args()
    {"create": cmd_create, "list": cmd_list, "history": cmd_history}[args.command](args)


if __name__ == "__main__":
    main()
