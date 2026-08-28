#!/usr/bin/env python3
"""
Generate stub .c files for the 4 F1AP CU source files.

The F1AP generated code (mouse07410 asn1c) uses ANY_t for open-type `value`
fields, but OAI source expects union-based access (ie->value.choice.X,
ie->value.present = ...IEs__value_PR_X). Replicating OAI's union-generating
asn1c by hand is impractical (per-IE unions across 8 messages). To get a
compiling+linking nr-softmodem, we stub the 4 CU-side F1AP files: each public
function (declared in the corresponding header) is replaced with `return 0;`.

F1AP CU<->DU signaling is non-functional with these stubs, but nr-softmodem
builds and links. Originals are git-tracked OAI source (recoverable).

Reads each f1ap_cu_*.h, extracts function declarations (multi-line, ending ';'),
emits a stub .c that includes the header and defines each function as a no-op.
"""

import re
import os

F1AP_DIR = "/home/kongbai/openairinterface5g/openair2/F1AP"

# (header, source) pairs
# Both CU and DU sides are stubbed: the generated F1AP code uses ANY_t for the
# open-type `value` field, so every source file that touches value.choice.X
# (4 CU + 4 DU) is uncompilable without a union-generating asn1c.
PAIRS = [
    ("f1ap_cu_ue_context_management.h", "f1ap_cu_ue_context_management.c"),
    ("f1ap_cu_interface_management.h", "f1ap_cu_interface_management.c"),
    ("f1ap_cu_rrc_message_transfer.h", "f1ap_cu_rrc_message_transfer.c"),
    ("f1ap_cu_paging.h", "f1ap_cu_paging.c"),
    ("f1ap_du_ue_context_management.h", "f1ap_du_ue_context_management.c"),
    ("f1ap_du_interface_management.h", "f1ap_du_interface_management.c"),
    ("f1ap_du_rrc_message_transfer.h", "f1ap_du_rrc_message_transfer.c"),
    ("f1ap_du_paging.h", "f1ap_du_paging.c"),
]


def extract_decls(header_text):
    """Extract function declarations: lines starting a signature at col 0,
    continuing until ';'. Returns list of declaration strings (with types/params,
    WITHOUT the trailing ';')."""
    decls = []
    lines = header_text.splitlines()
    i = 0
    # A function decl line: starts at col 0 with a type keyword, contains '('
    decl_start = re.compile(r"^(int|void|bool|long|F1AP_[A-Za-z0-9_]+\s*\*?)\s+\*?[A-Za-z_]\w*\s*\(")
    while i < len(lines):
        line = lines[i]
        if decl_start.match(line):
            acc = [line]
            # accumulate until we hit a line ending with ';'
            while i < len(lines) and ";" not in lines[i]:
                i += 1
                if i < len(lines):
                    acc.append(lines[i])
            joined = " ".join(s.strip() for s in acc)
            # strip trailing ';'
            joined = joined.rstrip().rstrip(";").rstrip()
            decls.append(joined)
        i += 1
    return decls


def gen_stub(header_name, decls):
    out = f"""/* Auto-generated F1AP stub for RISC-V port.
 * Replaces {header_name}'s .c because mouse07410 asn1c emits ANY_t for
 * open-type `value`, making the union-based OAI source un-compilable.
 * F1AP CU<->DU signaling is non-functional; functions are no-ops. */
/* f1ap_common.h must precede the specific header: the F1AP headers declare
 * functions using instance_t / uint32_t / F1AP_F1AP_PDU_t but include nothing
 * themselves, relying on the .c to pull in prerequisites first. f1ap_common.h
 * -> oai_asn1.h -> assertions.h -> platform_types.h (instance_t) and pulls in
 * F1AP_F1AP-PDU.h (F1AP_F1AP_PDU_t) plus all F1AP_* message types. */
#include "f1ap_common.h"
#include "{header_name}"
#include <stddef.h>

"""
    for d in decls:
        out += f"{d} {{ return 0; }}\n\n"
    return out


def main():
    dry = os.environ.get("DRY_RUN", "1") == "1"
    for hdr, src in PAIRS:
        hp = os.path.join(F1AP_DIR, hdr)
        with open(hp) as f:
            decls = extract_decls(f.read())
        stub = gen_stub(hdr, decls)
        if dry:
            print(f"=== {src}: {len(decls)} stubs (DRY RUN) ===")
            for d in decls:
                print(f"  {d.split(chr(40))[0]} ...")
            continue
        sp = os.path.join(F1AP_DIR, src)
        bak = sp + ".orig"
        if not os.path.exists(bak):
            import shutil
            shutil.copy2(sp, bak)
        with open(sp, "w") as f:
            f.write(stub)
        print(f"Wrote {src}: {len(decls)} stubs (backup: {bak})")


if __name__ == "__main__":
    main()
