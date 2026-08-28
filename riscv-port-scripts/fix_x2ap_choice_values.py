#!/usr/bin/env python3
"""Thin wrapper: apply fix_choice_values.py to the generated X2AP headers.

Kept for replay compatibility. See fix_choice_values.py for details.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fix_choice_values  # noqa: E402

if __name__ == "__main__":
    sys.argv = ["fix_choice_values.py",
                "--dir", "/home/kongbai/openairinterface5g/build-riscv/openair2/X2AP/MESSAGES",
                "--prefix", "X2AP_", "--aliases"]
    sys.exit(fix_choice_values.main())
