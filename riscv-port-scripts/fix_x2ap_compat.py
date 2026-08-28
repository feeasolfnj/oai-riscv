#!/usr/bin/env python3
"""
Generate X2AP OAI compatibility header and modify generated X2AP headers
to use union-based value fields instead of ANY_t.

This is the same approach used for NGAP - the generated asn1c code uses
ANY_t for open types, but OAI source code expects union-based access
(value.choice.X).
"""

import os
import re
import glob

BUILD_DIR = "/home/kongbai/openairinterface5g/build-riscv/openair2/X2AP/MESSAGES"
SRC_DIR = "/home/kongbai/openairinterface5g/openair2/X2AP"
COMPAT_HEADER = os.path.join(BUILD_DIR, "X2AP_oai_compat.h")

# ============================================================
# Step 1: Scan X2AP source files for access patterns
# ============================================================

x2ap_sources = sorted(glob.glob(os.path.join(SRC_DIR, "*.c")))
all_source = ""
for f in x2ap_sources:
    with open(f) as fh:
        all_source += fh.read() + "\n"

# Find all value.choice.X access patterns and determine pointer vs value
# Pattern: value.choice.XXX followed by -> (pointer) or . or & or = or , or )
choice_members = {}  # name -> "pointer" or "value"

for m in re.finditer(r'value\.choice\.([A-Za-z0-9_]+)\s*(->|\.)', all_source):
    name = m.group(1)
    op = m.group(2)
    if op == '->':
        choice_members[name] = 'pointer'
    elif op == '.':
        if name not in choice_members or choice_members[name] != 'pointer':
            choice_members[name] = 'value'

# Also check for &value.choice.X (address-of = embedded value)
for m in re.finditer(r'&\s*(?:ie->|pdu->choice\.\w+\.)?value\.choice\.([A-Za-z0-9_]+)', all_source):
    name = m.group(1)
    if name not in choice_members or choice_members[name] != 'pointer':
        choice_members[name] = 'value'

# Also check for &pdu->choice.initiatingMessage.value.choice.X
for m in re.finditer(r'&\s*\w+->choice\.\w+\.value\.choice\.([A-Za-z0-9_]+)', all_source):
    name = m.group(1)
    if name not in choice_members or choice_members[name] != 'pointer':
        choice_members[name] = 'value'

# Simple scalar assignments: value.choice.X = something
for m in re.finditer(r'value\.choice\.([A-Za-z0-9_]+)\s*=(?!=)', all_source):
    name = m.group(1)
    if name not in choice_members:
        choice_members[name] = 'value'

print(f"Found {len(choice_members)} choice members:")
for name, kind in sorted(choice_members.items()):
    print(f"  {name}: {kind}")

# ============================================================
# Step 2: Find all IEs_t types
# ============================================================

ies_types = set()
for m in re.finditer(r'X2AP_[A-Za-z0-9_]+IEs_t\b', all_source):
    ies_types.add(m.group(0))
for m in re.finditer(r'X2AP_[A-Za-z0-9_]+_IEs_t\b', all_source):
    ies_types.add(m.group(0))

print(f"\nFound {len(ies_types)} IEs_t types")

# ============================================================
# Step 3: Find all message types (for InitiatingMessage/SuccessfulOutcome/UnsuccessfulOutcome unions)
# ============================================================

# InitiatingMessage message types
init_msg_types = []
for m in re.finditer(r'X2AP_InitiatingMessage__value_PR_(\w+)', all_source):
    init_msg_types.append(m.group(1))
init_msg_types = sorted(set(init_msg_types))

# SuccessfulOutcome message types
success_msg_types = []
for m in re.finditer(r'X2AP_SuccessfulOutcome__value_PR_(\w+)', all_source):
    success_msg_types.append(m.group(1))
success_msg_types = sorted(set(success_msg_types))

# UnsuccessfulOutcome message types
unsuccess_msg_types = []
for m in re.finditer(r'X2AP_UnsuccessfulOutcome__value_PR_(\w+)', all_source):
    unsuccess_msg_types.append(m.group(1))
unsuccess_msg_types = sorted(set(unsuccess_msg_types))

print(f"\nInitiatingMessage types: {init_msg_types}")
print(f"SuccessfulOutcome types: {success_msg_types}")
print(f"UnsuccessfulOutcome types: {unsuccess_msg_types}")

# ============================================================
# Step 4: Find all PR enum values needed
# ============================================================

pr_enums = set()
for m in re.finditer(r'X2AP_[A-Za-z0-9_]+_PR_[A-Za-z0-9_]+', all_source):
    pr_enums.add(m.group(0))

# Remove the ones that are already X2AP_PDU_PR (already defined in generated code)
pr_enums.discard('X2AP_X2AP_PDU_PR_NOTHING')
pr_enums.discard('X2AP_X2AP_PDU_PR_initiatingMessage')
pr_enums.discard('X2AP_X2AP_PDU_PR_successfulOutcome')
pr_enums.discard('X2AP_X2AP_PDU_PR_unsuccessfulOutcome')

print(f"\nFound {len(pr_enums)} PR enum values needed")

# ============================================================
# Step 5: Find all Cause constants needed
# ============================================================

cause_constants = set()
for m in re.finditer(r'X2AP_Cause[A-Za-z0-9_]+', all_source):
    s = m.group(0)
    if s not in ('X2AP_Cause_PR', 'X2AP_Cause_PR_t', 'X2AP_Cause_t', 'X2AP_Cause_PR_misc',
                 'X2AP_Cause_PR_protocol', 'X2AP_Cause_PR_radioNetwork', 'X2AP_Cause_PR_transport'):
        cause_constants.add(s)

print(f"\nCause constants: {cause_constants}")

# ============================================================
# Step 6: Check which generated headers exist for message types
# ============================================================

def header_exists(type_name):
    """Check if a generated header exists for a type."""
    # Try different file naming conventions
    candidates = [
        os.path.join(BUILD_DIR, f"X2AP_{type_name}.h"),
        os.path.join(BUILD_DIR, f"X2AP_{type_name.replace('_', '-')}.h"),
    ]
    for c in candidates:
        if os.path.exists(c):
            return True
    return False

# ============================================================
# Step 7: Generate X2AP_oai_compat.h
# ============================================================

# Build includes for all choice member types
includes = []
include_types = set()

# Map choice member names to header file names
# Many of these are compound types that have generated headers
for name in sorted(choice_members.keys()):
    # Try to find the header file
    # The type might be X2AP_<name>_t with header X2AP_<name>.h
    # or the name might use hyphens in the ASN.1 definition
    type_name = name
    # Check various header naming patterns
    for hname in [f"X2AP_{type_name}.h", f"X2AP_{type_name.replace('_', '-')}.h"]:
        if os.path.exists(os.path.join(BUILD_DIR, hname)):
            include_types.add(hname)
            break

# Also include headers for IEs types that are used as IE_TYPE in FIND_PROTOCOLIE_BY_ID
# These need to be typedef'd to X2AP_ProtocolIE_Field_t

header = """/* Auto-generated X2AP OAI compatibility header
 *
 * This header provides OAI-compatible type definitions for X2AP protocol.
 * The generated asn1c code uses ANY_t for open types, but OAI source code
 * expects union-based access (value.choice.X).
 */
#ifndef X2AP_OAI_COMPAT_H
#define X2AP_OAI_COMPAT_H

#include "constr_TYPE.h"
#include <asn_application.h>
#include <ANY.h>
#include "OCTET_STRING.h"
#include "X2AP_ProcedureCode.h"
#include "X2AP_Criticality.h"
#include "X2AP_ProtocolIE-ID.h"
#include "X2AP_Cause.h"

/* Include generated message type headers */
"""

for h in sorted(include_types):
    header += f'#include "{h}"\n'

# Add includes for message types used in InitiatingMessage/SuccessfulOutcome/UnsuccessfulOutcome
all_msg_types = set(init_msg_types + success_msg_types + unsuccess_msg_types)
msg_includes = set()
for mt in all_msg_types:
    for hname in [f"X2AP_{mt}.h", f"X2AP_{mt.replace('_', '-')}.h"]:
        if os.path.exists(os.path.join(BUILD_DIR, hname)):
            msg_includes.add(hname)
            break

for h in sorted(msg_includes):
    if h not in include_types:
        header += f'#include "{h}"\n'

header += """
#include "X2AP_X2AP-PDU.h"
#include "X2AP_InitiatingMessage.h"
#include "X2AP_SuccessfulOutcome.h"
#include "X2AP_UnsuccessfulOutcome.h"

#ifdef __cplusplus
extern "C" {
#endif

/* ============================================================
 * Missing ProcedureCode and ProtocolIE-ID constants
 * (already in X2AP_asn_constant.h, included via x2ap_common.h)
 * ============================================================ */

/* ============================================================
 * Missing PR enum values
 * ============================================================ */

"""

# Add PR enum defines - use arbitrary unique values since they're just discriminators
pr_value = 0
for enum_name in sorted(pr_enums):
    # Skip if it's a _PR type (like X2AP_Cause_PR_t)
    if enum_name.endswith('_PR_t') or enum_name.endswith('_PR'):
        continue
    header += f"#define {enum_name} {pr_value}\n"
    pr_value += 1

# Add Cause constants
header += "\n/* ============================================================\n"
header += " * Missing Cause protocol/radio constants\n"
header += " * ============================================================\n\n"

cause_vals = {
    'X2AP_CauseProtocol_unspecified': 0,
    'X2AP_CauseProtocol_transfer_syntax_error': 1,
    'X2AP_CauseProtocol_abstract_syntax_error_falsely_constructed_message': 2,
    'X2AP_CauseProtocol_abstract_syntax_error_unsupported': 3,
    'X2AP_CauseProtocol_abstract_syntax_error_reject': 4,
    'X2AP_CauseProtocol_abstract_syntax_error_ignore_and_notify': 5,
    'X2AP_CauseProtocol_message_not_compatible_with_receiver_state': 6,
    'X2AP_CauseProtocol_abstract_syntax_error_falsely_constructed_message_v1620': 7,
    'X2AP_CauseProtocol_unspecified_v1620': 8,
    'X2AP_CauseMisc_unspecified': 0,
    'X2AP_CauseMisc_control_processing_overload': 1,
    'X2AP_CauseMisc_not_enough_user_plane_processing_resources': 2,
    'X2AP_CauseMisc_hardware_failure': 3,
    'X2AP_CauseMisc_om_intervention': 4,
    'X2AP_CauseMisc_unknown_PLMN': 5,
    'X2AP_CauseRadioNetwork_handover_desirable_for_radio_reasons': 0,
    'X2AP_CauseRadioNetwork_radio_connection_with_UE_lost': 1,
    'X2AP_CauseRadioNetwork_unspecified': 2,
    'X2AP_CauseRadioNetwork_handover_desirable_for_radio_reasons_v1360': 3,
    'X2AP_CauseRadioNetwork_trelocprep_expiry': 4,
    'X2AP_CauseRadioNetwork_tx2relocoverall_expiry': 5,
    'X2AP_CauseRadioNetwork_tDCprep_expiry': 6,
    'X2AP_CauseRadioNetwork_tDCoverall_expiry': 7,
    'X2AP_CauseRadioNetwork_x2_reset': 8,
    'X2AP_CauseRadioNetwork_x2_reset_v1360': 9,
}

for name in sorted(cause_constants):
    if name in cause_vals:
        header += f"#define {name} {cause_vals[name]}\n"
    else:
        header += f"#define {name} 0\n"

# Add ServedCells__Member type
header += """
/* ============================================================
 * ServedCells__Member type
 * ============================================================ */

#include "X2AP_ServedCells.h"

typedef struct X2AP_ServedCells_Member X2AP_ServedCells_Member_t;
#define ServedCells__Member X2AP_ServedCells_Member

"""

# Build the IE value union
header += """
/* ============================================================
 * IE value union - OAI accesses value.choice.X
 * ============================================================ */

typedef struct X2AP_IE_Value {
    long present;  /* discriminator */
    union X2AP_IE_Value_u {
        void *ptr;

"""

for name in sorted(choice_members.keys()):
    kind = choice_members[name]
    if kind == 'pointer':
        header += f"        struct X2AP_{name} *{name};\n"
    else:
        header += f"        struct X2AP_{name} {name};\n"

header += """    } choice;
} X2AP_IE_Value_t;

/* ============================================================
 * struct X2AP_ProtocolIE_Field - complete definition
 * The generated containers use A_SEQUENCE_OF(struct X2AP_ProtocolIE_Field)
 * which is forward-declared. We define it here.
 * ============================================================ */

struct X2AP_ProtocolIE_Field {
    X2AP_ProtocolIE_ID_t     id;
    X2AP_Criticality_t       criticality;
    X2AP_IE_Value_t  value;
    asn_struct_ctx_t _asn_ctx;
};
typedef struct X2AP_ProtocolIE_Field X2AP_ProtocolIE_Field_t;

/* Typedef all IEs_t types to the generic IE field type */
"""

for t in sorted(ies_types):
    header += f"typedef X2AP_ProtocolIE_Field_t {t};\n"

# Add message type typedefs for types that might be missing
# These are usually defined in generated headers, but some might need aliases
header += """
/* ============================================================
 * asn1cSeqAdd / asn1cSequenceAdd macros
 * ============================================================ */

#ifndef asn1cSeqAdd
#define asn1cSeqAdd(seq, type, ptr) \\
    do { \\
        type *_tmp = (ptr); \\
        asn_sequence_add(&(seq)->list, _tmp); \\
    } while(0)
#endif

#ifndef asn1cSequenceAdd
#define asn1cSequenceAdd(list, type, var) \\
    type *var = calloc(1, sizeof(type)); \\
    if (!var) { /* allocation failed */ } \\
    asn_sequence_add(&(list)->list, var)
#endif

#ifdef __cplusplus
}
#endif

#endif /* X2AP_OAI_COMPAT_H */
"""

with open(COMPAT_HEADER, 'w') as f:
    f.write(header)

print(f"\nGenerated {COMPAT_HEADER} ({len(header)} bytes)")

# ============================================================
# Step 8: Modify X2AP_InitiatingMessage.h
# ============================================================

init_header_path = os.path.join(BUILD_DIR, "X2AP_InitiatingMessage.h")

# Forward declarations for message types
fwd_decls = "\n".join(f"struct X2AP_{t};" for t in init_msg_types)

# Union members for InitiatingMessage
union_members = ""
for t in init_msg_types:
    # Check if the source accesses this with -> or . or &
    pattern = rf'(?:&|->|\.)value\.choice\.{t}\s*(->|\.)'
    matches = re.findall(pattern, all_source)
    if '->' in matches:
        union_members += f"\t\tstruct X2AP_{t}\t *{t};\n"
    else:
        union_members += f"\t\tstruct X2AP_{t}\t {t};\n"

init_content = f"""/*
 * Generated by asn1c-1.0.0 (http://lionet.info/asn1c)
 * Modified for OAI compatibility - uses proper union for value field
 */

#ifndef\t_X2AP_InitiatingMessage_H_
#define\t_X2AP_InitiatingMessage_H_

#include <asn_application.h>
#include "X2AP_ProcedureCode.h"
#include "X2AP_Criticality.h"
#include "constr_SEQUENCE.h"
#include "X2AP_oai_compat.h"

#ifdef __cplusplus
extern "C" {{
#endif

/* Forward declarations for message types */
{fwd_decls}

/* X2AP_InitiatingMessage value */
typedef struct X2AP_InitiatingMessage_value {{
\tlong present;\t/* discriminator */
\tunion X2AP_InitiatingMessage_value_u {{
{union_members}\t\t/* Extensions may appear below */
\t}} choice;

\tasn_struct_ctx_t _asn_ctx;
}} X2AP_InitiatingMessage_value_t;

/* X2AP_InitiatingMessage */
typedef struct X2AP_InitiatingMessage {{
\tX2AP_ProcedureCode_t\t procedureCode;
\tX2AP_Criticality_t\t criticality;
\tX2AP_InitiatingMessage_value_t\t value;

\tasn_struct_ctx_t _asn_ctx;
}} X2AP_InitiatingMessage_t;

/* PR enum for value.present */
typedef enum X2AP_InitiatingMessage__value_PR {{
\tX2AP_InitiatingMessage__value_PR_NOTHING,
"""

for i, t in enumerate(init_msg_types):
    init_content += f"\tX2AP_InitiatingMessage__value_PR_{t},\n"

init_content += """} X2AP_InitiatingMessage__value_PR_t;

/* Implementation */
extern asn_TYPE_descriptor_t asn_DEF_X2AP_InitiatingMessage;
extern asn_SEQUENCE_specifics_t asn_SPC_X2AP_InitiatingMessage_1;
extern asn_TYPE_member_t asn_MBR_X2AP_InitiatingMessage_1[3];

#ifdef __cplusplus
}
#endif

#endif\t/* _X2AP_InitiatingMessage_H_ */
#include <asn_internal.h>
"""

with open(init_header_path, 'w') as f:
    f.write(init_content)
print(f"Modified {init_header_path}")

# ============================================================
# Step 9: Modify X2AP_SuccessfulOutcome.h
# ============================================================

success_header_path = os.path.join(BUILD_DIR, "X2AP_SuccessfulOutcome.h")

fwd_decls_s = "\n".join(f"struct X2AP_{t};" for t in success_msg_types)

union_members_s = ""
for t in success_msg_types:
    pattern = rf'(?:&|->|\.)value\.choice\.{t}\s*(->|\.)'
    matches = re.findall(pattern, all_source)
    if '->' in matches:
        union_members_s += f"\t\tstruct X2AP_{t}\t *{t};\n"
    else:
        union_members_s += f"\t\tstruct X2AP_{t}\t {t};\n"

success_content = f"""/*
 * Generated by asn1c-1.0.0 (http://lionet.info/asn1c)
 * Modified for OAI compatibility - uses proper union for value field
 */

#ifndef\t_X2AP_SuccessfulOutcome_H_
#define\t_X2AP_SuccessfulOutcome_H_

#include <asn_application.h>
#include "X2AP_ProcedureCode.h"
#include "X2AP_Criticality.h"
#include "constr_SEQUENCE.h"
#include "X2AP_oai_compat.h"

#ifdef __cplusplus
extern "C" {{
#endif

/* Forward declarations for message types */
{fwd_decls_s}

/* X2AP_SuccessfulOutcome value */
typedef struct X2AP_SuccessfulOutcome_value {{
\tlong present;\t/* discriminator */
\tunion X2AP_SuccessfulOutcome_value_u {{
{union_members_s}\t\t/* Extensions may appear below */
\t}} choice;

\tasn_struct_ctx_t _asn_ctx;
}} X2AP_SuccessfulOutcome_value_t;

/* X2AP_SuccessfulOutcome */
typedef struct X2AP_SuccessfulOutcome {{
\tX2AP_ProcedureCode_t\t procedureCode;
\tX2AP_Criticality_t\t criticality;
\tX2AP_SuccessfulOutcome_value_t\t value;

\tasn_struct_ctx_t _asn_ctx;
}} X2AP_SuccessfulOutcome_t;

/* PR enum for value.present */
typedef enum X2AP_SuccessfulOutcome__value_PR {{
\tX2AP_SuccessfulOutcome__value_PR_NOTHING,
"""

for i, t in enumerate(success_msg_types):
    success_content += f"\tX2AP_SuccessfulOutcome__value_PR_{t},\n"

success_content += """} X2AP_SuccessfulOutcome__value_PR_t;

/* Implementation */
extern asn_TYPE_descriptor_t asn_DEF_X2AP_SuccessfulOutcome;
extern asn_SEQUENCE_specifics_t asn_SPC_X2AP_SuccessfulOutcome_1;
extern asn_TYPE_member_t asn_MBR_X2AP_SuccessfulOutcome_1[3];

#ifdef __cplusplus
}
#endif

#endif\t/* _X2AP_SuccessfulOutcome_H_ */
#include <asn_internal.h>
"""

with open(success_header_path, 'w') as f:
    f.write(success_content)
print(f"Modified {success_header_path}")

# ============================================================
# Step 10: Modify X2AP_UnsuccessfulOutcome.h
# ============================================================

unsuccess_header_path = os.path.join(BUILD_DIR, "X2AP_UnsuccessfulOutcome.h")

fwd_decls_u = "\n".join(f"struct X2AP_{t};" for t in unsuccess_msg_types)

union_members_u = ""
for t in unsuccess_msg_types:
    union_members_u += f"\t\tstruct X2AP_{t}\t {t};\n"

unsuccess_content = f"""/*
 * Generated by asn1c-1.0.0 (http://lionet.info/asn1c)
 * Modified for OAI compatibility - uses proper union for value field
 */

#ifndef\t_X2AP_UnsuccessfulOutcome_H_
#define\t_X2AP_UnsuccessfulOutcome_H_

#include <asn_application.h>
#include "X2AP_ProcedureCode.h"
#include "X2AP_Criticality.h"
#include "constr_SEQUENCE.h"
#include "X2AP_oai_compat.h"

#ifdef __cplusplus
extern "C" {{
#endif

/* Forward declarations for message types */
{fwd_decls_u}

/* X2AP_UnsuccessfulOutcome value */
typedef struct X2AP_UnsuccessfulOutcome_value {{
\tlong present;\t/* discriminator */
\tunion X2AP_UnsuccessfulOutcome_value_u {{
{union_members_u}\t\t/* Extensions may appear below */
\t}} choice;

\tasn_struct_ctx_t _asn_ctx;
}} X2AP_UnsuccessfulOutcome_value_t;

/* X2AP_UnsuccessfulOutcome */
typedef struct X2AP_UnsuccessfulOutcome {{
\tX2AP_ProcedureCode_t\t procedureCode;
\tX2AP_Criticality_t\t criticality;
\tX2AP_UnsuccessfulOutcome_value_t\t value;

\tasn_struct_ctx_t _asn_ctx;
}} X2AP_UnsuccessfulOutcome_t;

/* PR enum for value.present */
typedef enum X2AP_UnsuccessfulOutcome__value_PR {{
\tX2AP_UnsuccessfulOutcome__value_PR_NOTHING,
"""

for i, t in enumerate(unsuccess_msg_types):
    unsuccess_content += f"\tX2AP_UnsuccessfulOutcome__value_PR_{t},\n"

unsuccess_content += """} X2AP_UnsuccessfulOutcome__value_PR_t;

/* Implementation */
extern asn_TYPE_descriptor_t asn_DEF_X2AP_UnsuccessfulOutcome;
extern asn_SEQUENCE_specifics_t asn_SPC_X2AP_UnsuccessfulOutcome_1;
extern asn_TYPE_member_t asn_MBR_X2AP_UnsuccessfulOutcome_1[3];

#ifdef __cplusplus
}
#endif

#endif\t/* _X2AP_UnsuccessfulOutcome_H_ */
#include <asn_internal.h>
"""

with open(unsuccess_header_path, 'w') as f:
    f.write(unsuccess_content)
print(f"Modified {unsuccess_header_path}")

# ============================================================
# Step 11: Modify x2ap_common.h to include compat header
# ============================================================

common_header_path = os.path.join(SRC_DIR, "x2ap_common.h")
with open(common_header_path) as f:
    common_content = f.read()

if 'X2AP_oai_compat.h' not in common_content:
    # Add include after the existing X2AP includes
    common_content = common_content.replace(
        '#include "X2AP_Cause.h"',
        '#include "X2AP_Cause.h"\n#include "X2AP_oai_compat.h"'
    )
    with open(common_header_path, 'w') as f:
        f.write(common_content)
    print(f"Modified {common_header_path} to include X2AP_oai_compat.h")
else:
    print(f"{common_header_path} already includes X2AP_oai_compat.h")

print("\n=== X2AP compat generation complete ===")
