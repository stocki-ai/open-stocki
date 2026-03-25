#!/usr/bin/env python3
"""
Self-diagnostic for Stocki skill. Verifies instant and quant modes work.

Usage:
    python3 stocki-diagnose.py

Runs two checks:
  1. Instant mode — asks a simple financial question
  2. Quant mode — creates a task, submits a run, checks status

Exit:   0 all passed, 1 any check failed
"""

import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
from _gateway import gateway_request


def check_instant():
    """Test instant mode with a simple question."""
    print("[1/2] Instant mode...", end=" ", flush=True)
    try:
        result = gateway_request(
            "POST",
            "/v1/instant",
            {"query": "what is S&P 500?", "timezone": "Asia/Shanghai"},
            timeout=120,
        )
        answer = result.get("answer", "")
        if answer:
            print(f"OK ({len(answer)} chars)")
            return True
        else:
            print("FAIL (empty answer)")
            return False
    except SystemExit:
        print("FAIL")
        return False


def check_quant():
    """Test quant mode: create task, submit run, check status."""
    print("[2/2] Quant mode...", end=" ", flush=True)
    task_name = f"_diagnose_{int(time.time())}"
    try:
        # Create task
        task = gateway_request("POST", "/v1/tasks", {"name": task_name}, timeout=30)
        task_id = task.get("task_id", "")
        if not task_id:
            print("FAIL (no task_id)")
            return False

        # Submit run
        run = gateway_request(
            "POST",
            f"/v1/tasks/{task_id}/runs",
            {"query": "list top 3 S&P 500 stocks by market cap", "timezone": "Asia/Shanghai"},
            timeout=30,
        )
        run_id = run.get("run_id", "")
        status = run.get("status", "")
        if not run_id:
            print("FAIL (no run_id)")
            return False

        # Check status (just verify the endpoint works, don't wait for completion)
        check = gateway_request("GET", f"/v1/tasks/{task_id}/runs/{run_id}", timeout=120)
        check_status = check.get("status", "")
        if check_status in ("queued", "running", "success"):
            print(f"OK (task={task_id[:8]}..., run={run_id[:8] if len(run_id) > 8 else run_id}..., status={check_status})")
            return True
        else:
            print(f"FAIL (unexpected status: {check_status})")
            return False
    except SystemExit:
        print("FAIL")
        return False


def main():
    print("Stocki Self-Diagnostic")
    print("=" * 40)

    passed = 0
    total = 2

    if check_instant():
        passed += 1
    if check_quant():
        passed += 1

    print("=" * 40)
    print(f"Result: {passed}/{total} passed")

    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
