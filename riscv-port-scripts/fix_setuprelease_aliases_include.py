#!/usr/bin/env python3
"""
fix_setuprelease_aliases_include.py

Problem:
  Generated asn1c headers in build-riscv/openair2/RRC/NR/MESSAGES/ were edited
  to declare fields with human-readable alias types such as
  `NR_SetupRelease_PathlossReferenceRSList_r16_t`. Those aliases are typedef'd
  in NR_SetupRelease_aliases.h, but the generated headers only include
  NR_SetupRelease.h (which defines the generic NR_SetupRelease_2173P*_t types).
  Result: "unknown type name 'NR_SetupRelease_..._t'" compile errors.

Fix:
  For every .h that references an alias type (NR_SetupRelease_<non-numeric>_t)
  or includes NR_SetupRelease.h, ensure it also includes
  NR_SetupRelease_aliases.h. We insert it right after the existing
  `#include "NR_SetupRelease.h"` line (or after asn_application.h if the
  SetupRelease include is absent).

Idempotent: skips files that already include the aliases header.
"""

import os
import re
import sys

MESSAGES_DIR = (
    "/home/kongbai/openairinterface5g/build-riscv/openair2/RRC/NR/MESSAGES"
)
ALIASES_INCLUDE = '#include "NR_SetupRelease_aliases.h"'
SETUPRELEASE_INCLUDE = '#include "NR_SetupRelease.h"'

# Match alias type usage like NR_SetupRelease_PDSCH_Config_t but NOT the
# generic NR_SetupRelease_2173P0_t / NR_SetupRelease_t itself.
ALIAS_TYPE_RE = re.compile(r"NR_SetupRelease_[A-Za-z][A-Za-z0-9_-]*_t")


def needs_aliases(path, content):
    if path.endswith("NR_SetupRelease_aliases.h"):
        return False
    if path.endswith("NR_SetupRelease.h"):
        return False
    if ALIASES_INCLUDE in content:
        return False  # already fixed
    if ALIAS_TYPE_RE.search(content):
        return True
    if SETUPRELEASE_INCLUDE in content:
        return True
    return False


def fix_file(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()
    if not needs_aliases(path, content):
        return False
    new_content = None
    # Preferred: insert right after the SetupRelease include line.
    if SETUPRELEASE_INCLUDE in content:
        new_content = content.replace(
            SETUPRELEASE_INCLUDE,
            SETUPRELEASE_INCLUDE + "\n" + ALIASES_INCLUDE,
            1,
        )
    else:
        # Fallback: insert after the first asn_application.h include, or after
        # the first #include line.
        lines = content.splitlines(keepends=True)
        insert_at = None
        for i, line in enumerate(lines):
            if line.startswith("#include"):
                insert_at = i + 1
                if "asn_application.h" in line:
                    break
        if insert_at is not None:
            lines.insert(insert_at, ALIASES_INCLUDE + "\n")
            new_content = "".join(lines)
    if new_content is None:
        return False
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)
    return True


def main():
    if not os.path.isdir(MESSAGES_DIR):
        print("ERROR: messages dir not found:", MESSAGES_DIR, file=sys.stderr)
        return 1
    fixed = []
    skipped = 0
    for name in sorted(os.listdir(MESSAGES_DIR)):
        if not name.endswith(".h"):
            continue
        path = os.path.join(MESSAGES_DIR, name)
        if fix_file(path):
            fixed.append(name)
        else:
            skipped += 1
    print("Fixed %d headers:" % len(fixed))
    for n in fixed:
        print("  " + n)
    print("Skipped %d headers (already OK or not relevant)" % skipped)
    return 0


if __name__ == "__main__":
    sys.exit(main())
