#!/usr/bin/env python3
"""
Ask Stocki a financial question (instant mode).

Usage:
    python3 stocki-instant.py <question> [--timezone Asia/Shanghai]

Stdout: formatted answer
Stderr: error messages
Exit:   0 success, 1 auth/client error, 2 service error, 3 rate limited/quota
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _gateway import format_for_wechat, gateway_request


def main():
    parser = argparse.ArgumentParser(description="Ask Stocki a financial question.")
    parser.add_argument("question", help="The question to ask")
    parser.add_argument(
        "--timezone",
        default="Asia/Shanghai",
        help="IANA timezone (default: Asia/Shanghai)",
    )
    args = parser.parse_args()

    result = gateway_request(
        "POST",
        "/v1/instant",
        {"question": args.question, "timezone": args.timezone},
        timeout=120,
    )

    answer = result.get("answer", "")
    if not answer:
        print("No answer returned.", file=sys.stderr)
        sys.exit(1)

    print(format_for_wechat(answer))


if __name__ == "__main__":
    main()
