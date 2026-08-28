#!/usr/bin/env python3
"""
fix_asn1c_include_order.py

Problem:
  asn1c-844f9ca (2026-07-24) generates alias-typedef headers like:

    #ifndef _X2AP_PLMN_Identity_H_
    #define _X2AP_PLMN_Identity_H_

    typedef OCTET_STRING_t X2AP_PLMN_Identity_t;   # uses OCTET_STRING_t ...

    #include <asn_application.h>
    /* Including external dependencies */
    #include <OCTET_STRING.h>                      # ... before it is defined

  i.e. the typedef appears BEFORE the external includes. In C the typedef's
  right-hand-side type must already be declared, so this fails to compile with
  "unknown type name 'OCTET_STRING_t'".

Fix:
  For every generated header in the given asn1c MESSAGES dirs, if a plain
  alias `typedef ..._t` line appears before the first `#include`, move that
  line to just after the last `#include` of the file (still inside the
  include guard). Idempotent.

Usage:
  python3 fix_asn1c_include_order.py [dir ...]
  default dirs: the asn1c-generated MESSAGES dirs under build-riscv/openair*
"""

import os
import re
import sys

DEFAULT_DIRS = [
    "/home/kongbai/openairinterface5g/build-riscv/openair2/X2AP/MESSAGES",
    "/home/kongbai/openairinterface5g/build-riscv/openair2/F1AP/MESSAGES",
    "/home/kongbai/openairinterface5g/build-riscv/openair2/E1AP/MESSAGES",
    "/home/kongbai/openairinterface5g/build-riscv/openair3/S1AP/MESSAGES",
    "/home/kongbai/openairinterface5g/build-riscv/openair3/M3AP/MESSAGES",
    "/home/kongbai/openairinterface5g/build-riscv/openair3/M2AP/MESSAGES",
    "/home/kongbai/openairinterface5g/build-riscv/openair3/NGAP/MESSAGES",
]

# A plain alias typedef: starts with "typedef", but is NOT typedef struct/enum/union
ALIAS_TYPEDEF_RE = re.compile(r"^\s*typedef\s+(?!struct\b|enum\b|union\b)\S.*;\s*$")
INCLUDE_RE = re.compile(r"^\s*#\s*include\s*[<\"]")


def fix_file(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()

    # Locate include block: first and last #include lines.
    include_idx = [i for i, ln in enumerate(lines) if INCLUDE_RE.match(ln)]
    if not include_idx:
        return False
    first_inc, last_inc = include_idx[0], include_idx[-1]

    # Locate plain alias typedef line that appears BEFORE the first include.
    move = None
    for i in range(0, first_inc):
        if ALIAS_TYPEDEF_RE.match(lines[i]):
            # Ensure it is not inside a #if block that has an #endif before
            # the first include (asn1c does not emit those for aliases).
            move = i
            break
    if move is None:
        return False

    line = lines.pop(move)
    # Insert after the last include line; keep the trailing newline.
    lines.insert(last_inc, line)
    with open(path, "w", encoding="utf-8") as f:
        f.writelines(lines)
    return True


def main():
    dirs = sys.argv[1:] or DEFAULT_DIRS
    total_fixed = 0
    for d in dirs:
        if not os.path.isdir(d):
            print("SKIP (not a dir):", d)
            continue
        fixed = []
        for name in sorted(os.listdir(d)):
            if not name.endswith(".h"):
                continue
            path = os.path.join(d, name)
            if fix_file(path):
                fixed.append(name)
        total_fixed += len(fixed)
        print("Dir %s: fixed %d headers" % (d, len(fixed)))
        for n in fixed[:40]:
            print("  " + n)
        if len(fixed) > 40:
            print("  ... and %d more" % (len(fixed) - 40))
    print("TOTAL fixed: %d" % total_fixed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
