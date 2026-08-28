#!/usr/bin/env python3
"""
fix_x2ap_compat_aliases.py

Remove the `typedef X2AP_ProtocolIE_Field_t X2AP_*_IEs_t;` alias block from the
build's X2AP_oai_compat.h.

asn1c-844f9ca generates real, per-procedure IEs structs in
X2AP_ProtocolIE-Field.h (typedef struct X2AP_XXX_IEs { id; criticality;
X2AP_XXX_IEs__value value; asn_struct_ctx_t _asn_ctx; } X2AP_XXX_IEs_t;).
Those structs are layout-compatible with OAI's `ie->value.choice.X` access, so
re-aliasing the same names here triggers
"error: redefinition of typedef 'X2AP_XXX_IEs_t'".

Idempotent: only touches the exact alias lines.

Usage: python3 fix_x2ap_compat_aliases.py
"""

import re
import sys

COMPAT_H = "/home/kongbai/openairinterface5g/build-riscv/openair2/X2AP/MESSAGES/X2AP_oai_compat.h"

ALIAS_RE = re.compile(r"^typedef X2AP_ProtocolIE_Field_t X2AP_\w+_IEs_t;\s*$")


def main():
    with open(COMPAT_H) as f:
        lines = f.readlines()

    out = [ln for ln in lines if not ALIAS_RE.match(ln)]
    removed = len(lines) - len(out)
    if removed:
        with open(COMPAT_H, "w") as f:
            f.writelines(out)
        print(f"{COMPAT_H}: removed {removed} alias typedef line(s)")
    else:
        print(f"{COMPAT_H}: no alias typedefs to remove (already fixed)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
