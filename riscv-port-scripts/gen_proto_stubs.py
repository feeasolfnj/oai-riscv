#!/usr/bin/env python3
"""
Generate no-op stub .c files for OAI protocol source files that are
incompatible with the mouse07410 asn1c output used in the RISC-V port.

The generated asn1c code emits ANY_t for open-type `value` fields and uses
enum/API names that differ from what the OAI source expects (union-based
value.choice.X access, ASFM_* constants, asn_encode_to_new_buffer_result_t,
ATS_CANONICAL_XER, M2AP_ProcedureCode_id_* enum constants, etc.). Fixing each
source file individually is impractical, so we stub every affected source file:
each public function (declared in the corresponding header) becomes `return 0;`
(void functions get an empty body). This lets nr-softmodem compile and link.

Affected protocols (none are needed for a standalone 5G gNB to *run*):
  - F1AP  : CU<->DU signaling (4 CU + 4 DU files)
  - S1AP  : LTE S1 eNB<->MME (6 files + decoder)
  - M2AP  : MBMS signaling   (4 files + decoder)

For each stub, the protocol's *_common.h is included BEFORE the specific header
because the OAI protocol headers declare functions using instance_t / uint32_t /
<PROTO>_PDU_t but include nothing themselves -- they rely on the .c to pull in
prerequisites first. *_common.h -> oai_asn1.h -> assertions.h -> platform_types.h
(instance_t) and pulls in the <PROTO>_PDU header (<PROTO>_PDU_t) plus all
message types.

Declarations are deduplicated by function name: some OAI headers re-declare the
same function twice (e.g. f1ap_du_ue_context_management.h declares
DU_send_UE_CONTEXT_SETUP_RESPONSE at both line 39 and 88), which would otherwise
produce a "redefinition" error in the stub.
"""

import re
import os
import shutil

# Each protocol: directory, common header (prerequisite), and (header, source) pairs.
PROTOCOLS = [
    {
        "dir": "/home/kongbai/openairinterface5g/openair2/F1AP",
        "common": "f1ap_common.h",
        "pairs": [
            ("f1ap_cu_ue_context_management.h", "f1ap_cu_ue_context_management.c"),
            ("f1ap_cu_interface_management.h", "f1ap_cu_interface_management.c"),
            ("f1ap_cu_rrc_message_transfer.h", "f1ap_cu_rrc_message_transfer.c"),
            ("f1ap_cu_paging.h", "f1ap_cu_paging.c"),
            ("f1ap_du_ue_context_management.h", "f1ap_du_ue_context_management.c"),
            ("f1ap_du_interface_management.h", "f1ap_du_interface_management.c"),
            ("f1ap_du_rrc_message_transfer.h", "f1ap_du_rrc_message_transfer.c"),
            ("f1ap_du_paging.h", "f1ap_du_paging.c"),
        ],
    },
    {
        "dir": "/home/kongbai/openairinterface5g/openair3/S1AP",
        "common": "s1ap_common.h",
        # intertask_interface.h pulls in s1ap_messages_types.h, which defines
        # the lowercase s1ap_*_t message structs (s1ap_ue_release_complete_t,
        # s1ap_ue_release_req_t, ...) used in the S1AP source headers.
        # s1ap_eNB_defs.h defines s1ap_eNB_mme_data_t (used in
        # s1ap_eNB_handlers.h's s1ap_handle_s1_setup_message signature); the
        # original .c included it before the handlers header.
        "extra_includes": ["intertask_interface.h", "s1ap_eNB_defs.h"],
        "pairs": [
            ("s1ap_eNB.h", "s1ap_eNB.c"),
            ("s1ap_eNB_context_management_procedures.h", "s1ap_eNB_context_management_procedures.c"),
            ("s1ap_eNB_handlers.h", "s1ap_eNB_handlers.c"),
            ("s1ap_eNB_nas_procedures.h", "s1ap_eNB_nas_procedures.c"),
            ("s1ap_eNB_overload.h", "s1ap_eNB_overload.c"),
            ("s1ap_eNB_trace.h", "s1ap_eNB_trace.c"),
            ("s1ap_eNB_decoder.h", "s1ap_eNB_decoder.c"),
            ("s1ap_eNB_encoder.h", "s1ap_eNB_encoder.c"),
        ],
    },
    {
        "dir": "/home/kongbai/openairinterface5g/openair2/M2AP",
        "common": "m2ap_common.h",
        # m2ap_eNB_defs.h / m2ap_MCE_defs.h define the m2ap_{eNB,MCE}_instance_t
        # and m2ap_{eNB,MCE}_data_t types used in the M2AP source headers
        # (e.g. m2ap_eNB_interface_management.h's eNB_send_M2_SETUP_REQUEST takes
        # m2ap_eNB_instance_t*). The headers don't include the defs themselves;
        # the original .c files pulled them in transitively.
        "extra_includes": ["m2ap_eNB_defs.h", "m2ap_MCE_defs.h"],
        "pairs": [
            ("m2ap_MCE_generate_messages.h", "m2ap_MCE_generate_messages.c"),
            ("m2ap_MCE_interface_management.h", "m2ap_MCE_interface_management.c"),
            ("m2ap_eNB_generate_messages.h", "m2ap_eNB_generate_messages.c"),
            ("m2ap_eNB_interface_management.h", "m2ap_eNB_interface_management.c"),
            ("m2ap_decoder.h", "m2ap_decoder.c"),
        ],
    },
    {
        "dir": "/home/kongbai/openairinterface5g/openair2/E1AP",
        "common": "e1ap_common.h",
        # E1AP has the same mouse07410-asn1c incompatibilities as F1AP: the
        # generated code uses ANY_t for open-type `value` (no .present/.choice
        # union members) and defines E1AP_ProcedureCode_t as a plain `long`
        # (NativeInteger) with NO E1AP_ProcedureCode_id_* enum constants, so
        # OAI's union-based e1ap.c and e1ap_common.c are un-compilable.
        # e1ap_api.c is higher-level (no direct ASN.1 value/enum access) and
        # compiles unchanged, so it is NOT stubbed. e1ap_setup.c is not in the
        # E1AP CMakeLists target list, so it is not built. e1ap_common.c's only
        # external-linkage global (transacID[]) is not referenced outside that
        # file, and e1ap.c's internal extract_*/fill_* helpers have no external
        # references, so stubbing drops no symbols needed at link time.
        "pairs": [
            ("e1ap.h", "e1ap.c"),
            ("e1ap_common.h", "e1ap_common.c"),
            ("e1ap_api.h", "e1ap_api.c"),
        ],
    },
    {
        "dir": "/home/kongbai/openairinterface5g/openair3/M3AP",
        "common": "m3ap_common.h",
        # M3AP has the same mouse07410-asn1c incompatibilities: ANY_t for
        # open-type `value` (M3AP_InitiatingMessage.h: `ANY_t value;`) and an
        # empty M3AP_asn_constant.h (M3AP_ProcedureCode_t is a plain `long`
        # with no M3AP_ProcedureCode_id_* constants). M3AP is the M3 (MBMS)
        # interface, non-essential for a standalone 5G gNB. All 14 sources in
        # the `m3ap` library (top-level CMakeLists.txt) are stubbed.
        # m3ap_MCE_defs.h / m3ap_MME_defs.h define the m3ap_{MCE,MME}_instance_t
        # and m3ap_{MCE,MME}_data_t types used in the M3AP source headers.
        # NB: m3ap_MCE_generate_messsages.c / m3ap_MME_generate_messages.c are
        # NOT in the m3ap library target, so they are not built (not stubbed).
        "extra_includes": ["m3ap_MCE_defs.h", "m3ap_MME_defs.h"],
        "pairs": [
            ("m3ap_common.h", "m3ap_common.c"),
            ("m3ap_decoder.h", "m3ap_decoder.c"),
            ("m3ap_encoder.h", "m3ap_encoder.c"),
            ("m3ap_MCE_handler.h", "m3ap_MCE_handler.c"),
            ("m3ap_MME_handler.h", "m3ap_MME_handler.c"),
            ("m3ap_MME.h", "m3ap_MME.c"),
            ("m3ap_MME_management_procedures.h", "m3ap_MME_management_procedures.c"),
            ("m3ap_MME_interface_management.h", "m3ap_MME_interface_management.c"),
            ("m3ap_MCE.h", "m3ap_MCE.c"),
            ("m3ap_MCE_management_procedures.h", "m3ap_MCE_management_procedures.c"),
            ("m3ap_MCE_interface_management.h", "m3ap_MCE_interface_management.c"),
            ("m3ap_itti_messaging.h", "m3ap_itti_messaging.c"),
            ("m3ap_ids.h", "m3ap_ids.c"),
            ("m3ap_timers.h", "m3ap_timers.c"),
        ],
    },
]

# A function declaration line: return type at col 0, then function name, then '('.
# Return type may be a keyword (int/void/bool/long/size_t/...), an ASN.1 uppercase
# type (F1AP_*/S1AP_*/M2AP_*/...), or a lowercase *_t typedef.
DECL_START = re.compile(
    r"^(int|void|bool|long|size_t|unsigned|char|double|float"
    r"|[A-Z][A-Za-z0-9_]+"      # F1AP_Foo, S1AP_Bar, ...
    r"|[A-Za-z_]\w*_t)"          # lowercase typedefs: instance_t, f1ap_setup_resp_t, ...
    r"\s+\*?[A-Za-z_]\w*\s*\("
)


def extract_func_name(decl):
    """Extract the function name (identifier right before the first '(')."""
    m = re.search(r"\*?\b([A-Za-z_]\w*)\s*\(", decl)
    return m.group(1) if m else None


def extract_decls(header_text):
    """Extract function declarations: lines at col 0 matching DECL_START,
    continuing until a line containing ';'. Deduplicate by function name.
    Strip trailing __attribute__((...)) clauses, which are legal on declarations
    but invalid on a definition body (gcc: 'attributes should be specified before
    the declarator in a function definition')."""
    decls = []
    seen = set()
    lines = header_text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if DECL_START.match(line):
            acc = [line]
            # Accumulate until we hit a line containing ';'.
            while i < len(lines) and ";" not in lines[i]:
                i += 1
                if i < len(lines):
                    acc.append(lines[i])
            joined = " ".join(s.strip() for s in acc)
            joined = joined.rstrip().rstrip(";").rstrip()
            # Drop trailing __attribute__ clauses (and anything after).
            joined = re.sub(r"\s+__attribute__\s*\(.*$", "", joined).rstrip()
            name = extract_func_name(joined)
            if name and name not in seen:
                seen.add(name)
                decls.append(joined)
        i += 1
    return decls


def gen_stub(common_header, header_name, decls, extra_includes=None):
    extra = "".join(f'#include "{h}"\n' for h in (extra_includes or []))
    out = f"""/* Auto-generated protocol stub for RISC-V port.
 * Replaces {header_name}'s .c: the mouse07410 asn1c output emits ANY_t for
 * open-type `value` and uses enum/API names incompatible with this OAI source
 * (union-based value.choice access, ASFM_* / asn_encode / ProcedureCode_id
 * constants). Functions are no-ops so nr-softmodem still builds and links. */
/* {common_header} must precede the specific header: the protocol headers
 * declare functions using instance_t / uint32_t / <PROTO>_PDU_t but include
 * nothing themselves, relying on the .c to pull in prerequisites first. */
#include "{common_header}"
{extra}#include "{header_name}"
#include <stddef.h>

"""
    for d in decls:
        # Functions returning exactly `void` get an empty body. Pointer- and
        # value-returning functions (including `void *`, used by ITTI task
        # entry points like F1AP_CU_task / s1ap_eNB_task / E1AP_CUUP_task)
        # must return a value: use `return 0;` (NULL for pointers). Emitting
        # `{ }` for a `void *` function compiles only with a warning in C and
        # returns garbage at runtime.
        if re.match(r"void\s+[A-Za-z_]", d):
            out += f"{d} {{ }}\n\n"
        else:
            out += f"{d} {{ return 0; }}\n\n"
    return out


def main():
    dry = os.environ.get("DRY_RUN", "1") == "1"
    total = 0
    for proto in PROTOCOLS:
        pdir = proto["dir"]
        common = proto["common"]
        for hdr, src in proto["pairs"]:
            hp = os.path.join(pdir, hdr)
            if not os.path.exists(hp):
                print(f"SKIP {src}: header {hdr} not found")
                continue
            with open(hp) as f:
                decls = extract_decls(f.read())
            if dry:
                print(f"=== {src}: {len(decls)} stubs (DRY RUN) ===")
                continue
            stub = gen_stub(common, hdr, decls, proto.get("extra_includes"))
            sp = os.path.join(pdir, src)
            bak = sp + ".orig"
            if not os.path.exists(bak):
                shutil.copy2(sp, bak)
            with open(sp, "w") as f:
                f.write(stub)
            print(f"Wrote {src}: {len(decls)} stubs (backup: {os.path.basename(bak)})")
            total += len(decls)
    if not dry:
        print(f"\nTotal: {total} stub functions generated.")


if __name__ == "__main__":
    main()
