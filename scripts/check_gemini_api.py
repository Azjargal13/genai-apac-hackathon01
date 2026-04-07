#!/usr/bin/env python3
"""Quick Gemini API health check.

Usage:
  python scripts/check_gemini_api.py
  python scripts/check_gemini_api.py --model gemini-3-flash-preview --prompt "Reply: OK"
"""

from __future__ import annotations

import argparse
import os
import sys

from dotenv import load_dotenv
from google import genai


def main() -> int:
    parser = argparse.ArgumentParser(description="Quick Gemini API check")
    parser.add_argument("--model", default="gemini-3-flash-preview")
    parser.add_argument("--prompt", default="Reply with exactly: OK")
    args = parser.parse_args()

    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("FAIL: GOOGLE_API_KEY is missing (.env not loaded or key not set).", file=sys.stderr)
        return 2

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=args.model,
            contents=args.prompt,
            config={"max_output_tokens": 32, "temperature": 0},
        )
        text = (response.text or "").strip()
        print("PASS: Gemini reachable")
        print(f"MODEL: {args.model}")
        print(f"REPLY: {text}")
        return 0
    except Exception as e:
        print("FAIL: Gemini call failed", file=sys.stderr)
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

