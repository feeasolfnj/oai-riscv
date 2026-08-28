#!/usr/bin/env python3
"""
fix_ext_access.py

The asn1c-oai generated code (both LTE and NR RRC) promotes ASN.1 extension
fields to DIRECT struct members, with NO ext1/ext2/ext3 wrapper structs.
Enum/constant names also drop the "__extN__" infix.

OAI source code, however, was written for standard asn1c which nests
extension fields under ext1/ext2/ext3. This script rewrites those accesses:

  x->ext1->Y   ->  x->Y
  x->ext2->Y   ->  x->Y
  x->ext3->Y   ->  x->Y
  __ext1__     ->  __        (in enum/constant identifiers)
  __ext2__     ->  __
  __ext3__     ->  __

Standalone "x->extN" guards (not followed by "->") are left for manual
handling, since they require knowing which direct member to check instead.

Operates on all .c files under openair2/LAYER2/MAC/ that contain ext1/ext2/ext3.
Idempotent for the patterns it transforms.
"""

import os
import re
import sys

MAC_DIR = "/home/kongbai/openairinterface5g/openair2/LAYER2/MAC"

# Order matters: do ->extN-> first, then __extN__
ARROW_RE = re.compile(r"->ext([0-9]+)->")
INFIX_RE = re.compile(r"__ext([0-9]+)__")


def transform(text):
    text = ARROW_RE.sub(r"->", text)
    text = INFIX_RE.sub(r"__", text)
    return text


def main():
    changed = []
    for name in sorted(os.listdir(MAC_DIR)):
        if not name.endswith(".c"):
            continue
        path = os.path.join(MAC_DIR, name)
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            orig = f.read()
        if not re.search(r"ext[0-9]", orig):
            continue
        new = transform(orig)
        if new != orig:
            with open(path, "w", encoding="utf-8") as f:
                f.write(new)
            # Count remaining standalone ->extN (not followed by ->)
            standalone = len(re.findall(r"->ext[0-9]+(?!->)", new))
            changed.append((name, standalone))
    print("Transformed %d files:" % len(changed))
    for n, s in changed:
        print("  %s  (remaining standalone ->extN: %d)" % (n, s))
    return 0


if __name__ == "__main__":
    sys.exit(main())
