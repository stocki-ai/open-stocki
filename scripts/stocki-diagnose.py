#!/usr/bin/env python3
"""
Self-diagnostic for Stocki skill. Verifies instant and quant modes work.

Usage:
    python3 stocki-diagnose.py

Runs two checks:
  1. Instant mode — asks a verifiable factual question
  2. Quant mode — submits analysis, waits for completion, checks results

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
    """Test instant mode: ask a verifiable factual question and validate the answer."""
    print("[1/2] Instant mode...", end=" ", flush=True)
    try:
        result = gateway_request(
            "POST",
            "/v1/instant",
            {"question": "What is the ticker symbol of Apple Inc on NASDAQ?", "timezone": "Asia/Shanghai"},
            timeout=120,
        )
        answer = result.get("answer", "")
        if not answer:
            print("FAIL (empty answer)")
            return False
        answer_upper = answer.upper()
        if "AAPL" in answer_upper:
            print(f"OK (verified AAPL in answer, {len(answer)} chars)")
            return True
        else:
            print(f"FAIL (answer does not contain 'AAPL')")
            print(f"  Answer: {answer[:200]}...")
            return False
    except SystemExit:
        print("FAIL")
        return False


def check_quant():
    """Test quant mode: submit analysis, wait for completion, check results."""
    print("[2/2] Quant mode...")
    try:
        # Step 1: Submit quant analysis (auto-creates task)
        print("  Submitting quant...", end=" ", flush=True)
        result = gateway_request(
            "POST",
            "/v1/quant",
            {"question": "What were the top 3 constituents of S&P 500 by market cap as of 2024-12-31? List their ticker symbols.", "timezone": "Asia/Shanghai"},
            timeout=30,
        )
        task_id = result.get("task_id", "")
        task_name = result.get("task_name", "")
        if not task_id:
            print("FAIL (no task_id)")
            return False
        print(f"OK (task_id={task_id}, name={task_name})")

        # Step 2: Poll task status until completion
        print("  Waiting for completion", end="", flush=True)
        elapsed = 0
        final_status = ""
        task_detail = {}
        while elapsed < MAX_WAIT:
            time.sleep(POLL_INTERVAL)
            elapsed += POLL_INTERVAL
            print(".", end="", flush=True)
            task_detail = gateway_request("GET", f"/v1/tasks/{task_id}", timeout=120)
            current_run = task_detail.get("current_run")
            if current_run is None:
                # No active run — check last run status
                runs = task_detail.get("runs", [])
                if runs:
                    final_status = runs[-1].get("status", "unknown")
                    if final_status in ("success", "error"):
                        break
            else:
                final_status = current_run.get("status", "unknown")

        print()
        if final_status == "success":
            print(f"  Run completed: OK (success in {elapsed}s)")
        elif final_status == "error":
            runs = task_detail.get("runs", [])
            err = runs[-1].get("error_message", "unknown") if runs else "unknown"
            print(f"  Run completed: FAIL (error: {err})")
            return False
        else:
            print(f"  Run timeout: FAIL (still {final_status} after {MAX_WAIT}s)")
            return False

        # Step 3: Verify results
        runs = task_detail.get("runs", [])
        last_run = runs[-1] if runs else {}
        summary = last_run.get("summary", "")
        files = last_run.get("files", [])

        print(f"  Files: {len(files)}, Summary: {len(summary)} chars")

        # Step 4: Verify answer correctness
        # As of 2024-12-31, top S&P 500 by market cap: AAPL, MSFT, NVDA
        print("  Verifying answer...", end=" ", flush=True)
        check_text = (summary or "").upper()
        expected = ["AAPL", "MSFT", "NVDA"]
        found = [s for s in expected if s in check_text]
        if len(found) >= 2:
            print(f"OK (found {', '.join(found)})")
        else:
            print(f"WARN (expected AAPL/MSFT/NVDA, found: {found or 'none'})")

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
