#!/usr/bin/env python3
"""
Self-diagnostic for Stocki skill. Verifies instant and quant modes work.

Usage:
    python3 stocki-diagnose.py

Runs two checks:
  1. Instant mode — asks a simple financial question
  2. Quant mode — creates a task, submits a run, waits for completion, downloads report

Exit:   0 all passed, 1 any check failed
"""

import os
import sys
import time

MAX_WAIT = 600  # 10 minutes max wait for quant run
POLL_INTERVAL = 30  # seconds between status checks

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
    """Test quant mode: create task, submit run, wait for completion, download report."""
    print("[2/2] Quant mode...")
    task_name = f"_diagnose_{int(time.time())}"
    try:
        # Step 1: Create task
        print("  Creating task...", end=" ", flush=True)
        task = gateway_request("POST", "/v1/tasks", {"name": task_name}, timeout=30)
        task_id = task.get("task_id", "")
        if not task_id:
            print("FAIL (no task_id)")
            return False
        print(f"OK ({task_id[:8]}...)")

        # Step 2: Submit run
        print("  Submitting run...", end=" ", flush=True)
        run = gateway_request(
            "POST",
            f"/v1/tasks/{task_id}/runs",
            {"query": "list top 3 S&P 500 stocks by market cap", "timezone": "Asia/Shanghai"},
            timeout=30,
        )
        run_id = run.get("run_id", "")
        if not run_id:
            print("FAIL (no run_id)")
            return False
        print(f"OK ({run_id[:8] if len(run_id) > 8 else run_id}...)")

        # Step 3: Poll until completion
        print("  Waiting for completion", end="", flush=True)
        elapsed = 0
        final_status = ""
        while elapsed < MAX_WAIT:
            time.sleep(POLL_INTERVAL)
            elapsed += POLL_INTERVAL
            print(".", end="", flush=True)
            check = gateway_request("GET", f"/v1/tasks/{task_id}/runs/{run_id}", timeout=120)
            final_status = check.get("status", "unknown")
            if final_status in ("success", "error"):
                break

        print()
        if final_status == "success":
            print(f"  Run completed: OK (success in {elapsed}s)")
        elif final_status == "error":
            msg = check.get("message", "unknown error")
            print(f"  Run completed: FAIL (error: {msg})")
            return False
        else:
            print(f"  Run timeout: FAIL (still {final_status} after {MAX_WAIT}s)")
            return False

        # Step 4: Check reports
        print("  Checking reports...", end=" ", flush=True)
        reports = gateway_request("GET", f"/v1/tasks/{task_id}/reports", timeout=300)
        report_list = reports.get("reports", [])
        if not report_list:
            print("WARN (no reports, but run succeeded)")
            return True

        # Step 5: Download first report
        first = report_list[0].get("filename", "")
        print(f"OK ({len(report_list)} file(s))")
        print(f"  Downloading '{first}'...", end=" ", flush=True)
        dl = gateway_request("GET", f"/v1/tasks/{task_id}/reports/{first}", timeout=300)
        content = dl.get("content", "")
        if content:
            print(f"OK ({len(content)} chars)")
        else:
            print("FAIL (empty content)")
            return False

        return True
    except SystemExit:
        print(" FAIL")
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
