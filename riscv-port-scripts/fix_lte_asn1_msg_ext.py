#!/usr/bin/env python3
"""
Fix LTE asn1_msg.c for asn1c-oai flattened extension members.

The asn1c-oai generated LTE RRC structs promote ASN.1 extension fields to
DIRECT members (no ext1/ext2/ext4/ext7 wrapper structs). OAI source was
written for standard asn1c which nests them under extN wrappers. This script:

  1. DELETES wrapper-allocation / wrapper-memset lines that target a non-existent
     extN member, e.g.:
       x->ext1 = calloc(1, sizeof(struct LTE_X__ext1));
       memset(x->ext1, 0, sizeof(struct LTE_X__ext1));
       x->ext1 = NULL;
     (These reference a member that no longer exists. With flattening the
      promoted members default to NULL via the parent's calloc, so the
      assignment is redundant/invalid.)

  2. TRANSFORMS extN indirection in field access:
       x.extN->FIELD   ->  x.FIELD        (dot-ext-arrow)
       (x->extN)->FIELD ->  x->FIELD       (MBSFN parenthesised form)
       ((x)->extN)->FIELD -> (x)->FIELD    (MBSFN double-paren form)

Lines are only deleted when extN is the LVALUE / memset target (extN immediately
followed by '=' or ','), never when extN is an intermediate (extN->FIELD).
Comment-only lines are never deleted.
"""

import re
import sys

PATH = "/home/kongbai/openairinterface5g/openair2/RRC/LTE/MESSAGES/asn1_msg.c"

# Rule A: standalone extN assignment to calloc/CALLOC/NULL.
# extN must be preceded by '.' or '>' (from '->') to avoid matching substrings
# like "next1". extN immediately followed by whitespace+'=' (not '->').
RULE_A = re.compile(r"[.>]ext[0-9]+\s*=\s*(?:calloc|CALLOC|NULL\b)")

# Rule B: memset of the extN wrapper itself (extN is the memset target).
# extN must be immediately followed by ',' (not '->FIELD').
RULE_B = re.compile(r"memset\([^;]*?[.>]ext[0-9]+\s*,")

# Rule C: drop dot-ext-arrow indirection.  x.extN->FIELD -> x.FIELD
RULE_C = re.compile(r"\.ext[0-9]+->")

# Rule D: MBSFN parenthesised forms.
#   ( VAR->extN)->FIELD  ->  VAR->FIELD
RULE_D1 = re.compile(r"\(\s*([A-Za-z_]\w*)->ext[0-9]+\)->")
#   ((VAR)->extN)->FIELD -> (VAR)->FIELD
RULE_D2 = re.compile(r"\(\(([A-Za-z_]\w*)\)->ext[0-9]+\)->")


def is_comment(line):
    return line.lstrip().startswith("//")


def main():
    with open(PATH) as f:
        lines = f.readlines()

    kept = []
    deleted = []
    for i, line in enumerate(lines, 1):
        if is_comment(line):
            kept.append((i, line))
            continue
        if RULE_A.search(line) or RULE_B.search(line):
            deleted.append((i, line.rstrip("\n")))
            continue
        kept.append((i, line))

    # Rebuild text from kept lines (drop original line numbers).
    text = "".join(l for _, l in kept)

    before_ext = len(re.findall(r"ext[0-9]+", text))
    text = RULE_D1.sub(r"\1->", text)
    text = RULE_D2.sub(r"(\1)->", text)
    text = RULE_C.sub(".", text)
    after_ext = len(re.findall(r"ext[0-9]+", text))

    with open(PATH, "w") as f:
        f.write(text)

    print(f"Deleted {len(deleted)} standalone extN lines:")
    for n, s in deleted:
        print(f"  L{n}: {s.strip()[:90]}")
    print(f"\nTransformed: D1/D2/C  (extN occurrences {before_ext} -> {after_ext})")

    # Report any remaining extN references that are not in comments.
    remaining = []
    for i, line in enumerate(text.splitlines(), 1):
        if is_comment(line):
            continue
        if re.search(r"ext[0-9]+", line):
            remaining.append((i, line.strip()[:100]))
    print(f"\nRemaining non-comment extN references: {len(remaining)}")
    for n, s in remaining[:30]:
        print(f"  L{n}: {s}")


if __name__ == "__main__":
    main()
