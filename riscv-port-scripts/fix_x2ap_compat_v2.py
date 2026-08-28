#!/usr/bin/env python3
"""
Fix X2AP OAI compatibility header - version 2.
Handles simple types (long, OCTET_STRING_t, BIT_STRING_t, enums) correctly
and avoids circular includes.
"""

import os
import re
import glob

BUILD_DIR = "/home/kongbai/openairinterface5g/build-riscv/openair2/X2AP/MESSAGES"
SRC_DIR = "/home/kongbai/openairinterface5g/openair2/X2AP"
COMPAT_HEADER = os.path.join(BUILD_DIR, "X2AP_oai_compat.h")

# ============================================================
# Scan X2AP source files
# ============================================================

x2ap_sources = sorted(glob.glob(os.path.join(SRC_DIR, "*.c")))
all_source = ""
for f in x2ap_sources:
    with open(f) as fh:
        all_source += fh.read() + "\n"

# ============================================================
# Classify choice members: pointer vs value, and their C type
# ============================================================

# Types that are simple typedefs (not structs)
# These map X2AP type names to their C representation
SIMPLE_TYPES = {
    # INTEGER types -> long
    'UE_X2AP_ID': 'long',
    'UE_X2AP_ID_1': 'long',
    'SgNB_UE_X2AP_ID': 'long',
    'Old_eNB_UE_X2AP_ID': 'long',
    'New_eNB_UE_X2AP_ID': 'long',
    'MeNB_UE_X2AP_ID': 'long',
    'SeNB_UE_X2AP_ID': 'long',
    'E_RAB_ID': 'long',
    'E_RABs_ToBeSetup_Item': None,  # compound - has header
    # OCTET STRING types -> OCTET_STRING_t
    'MeNBtoSeNBContainer': 'OCTET_STRING_t',
    'MeNBtoSgNBContainer': 'OCTET_STRING_t',
    'SeNBtoMeNBContainer': 'OCTET_STRING_t',
    'SgNBtoMeNBContainer': 'OCTET_STRING_t',
    'TargeteNBtoSource_eNBTransparentContainer': 'OCTET_STRING_t',
    'SourceeNBtoTargeteNBTransparentContainer': 'OCTET_STRING_t',
    # BIT STRING types -> BIT_STRING_t (same as OCTET_STRING_t in asn1c)
    'SeNBSecurityKey': 'BIT_STRING_t',
    'SgNBSecurityKey': 'BIT_STRING_t',
    # Enum types
    'TimeToWait': 'X2AP_TimeToWait_t',
    'InitiatingNodeType_EndcX2Setup': 'X2AP_InitiatingNodeType_EndcX2Setup_t',
    'RespondingNodeType_EndcX2Setup': 'X2AP_RespondingNodeType_EndcX2Setup_t',
    'ResponseInformationSgNBReconfComp': 'X2AP_ResponseInformationSgNBReconfComp_t',
    'EUTRA_Mode_Info': 'X2AP_EUTRA_Mode_Info_t',
    # Simple scalar types
    'UEAggregateMaximumBitRate': None,  # compound
    'NRUESecurityCapabilities': None,  # compound
    'UESecurityCapabilities': None,  # compound
}

# Find all value.choice.X access patterns
choice_members = {}  # name -> "pointer" or "value"

# Check for -> access (pointer)
for m in re.finditer(r'value\.choice\.([A-Za-z0-9_]+)\s*->', all_source):
    name = m.group(1)
    choice_members[name] = 'pointer'

# Check for . access (value) - only set to value if not already pointer
for m in re.finditer(r'value\.choice\.([A-Za-z0-9_]+)\s*\.', all_source):
    name = m.group(1)
    if name not in choice_members:
        choice_members[name] = 'value'

# Check for & access (value)
for m in re.finditer(r'&\s*[\w>.-]*\.?value\.choice\.([A-Za-z0-9_]+)', all_source):
    name = m.group(1)
    if name not in choice_members:
        choice_members[name] = 'value'

# Check for = access (value/scalar)
for m in re.finditer(r'value\.choice\.([A-Za-z0-9_]+)\s*=(?!=)', all_source):
    name = m.group(1)
    if name not in choice_members:
        choice_members[name] = 'value'

# Also check pdu->choice.X.value.choice.Y patterns
for m in re.finditer(r'choice\.\w+\.value\.choice\.([A-Za-z0-9_]+)\s*->', all_source):
    name = m.group(1)
    choice_members[name] = 'pointer'
for m in re.finditer(r'choice\.\w+\.value\.choice\.([A-Za-z0-9_]+)\s*\.', all_source):
    name = m.group(1)
    if name not in choice_members:
        choice_members[name] = 'value'

# Force pointer access for known compound types that the source accesses with ->
# Let me re-check by looking at actual source lines
for name in list(choice_members.keys()):
    # Check if any line has value.choice.{name}->
    if re.search(rf'value\.choice\.{re.escape(name)}\s*->', all_source):
        choice_members[name] = 'pointer'

print("Choice members:")
for name, kind in sorted(choice_members.items()):
    print(f"  {name}: {kind}")

# ============================================================
# Find all IEs_t types
# ============================================================

ies_types = set()
for m in re.finditer(r'X2AP_[A-Za-z0-9_]+IEs_t\b', all_source):
    ies_types.add(m.group(0))
for m in re.finditer(r'X2AP_[A-Za-z0-9_]+_IEs_t\b', all_source):
    ies_types.add(m.group(0))

# ============================================================
# Find message types for InitiatingMessage/SuccessfulOutcome/UnsuccessfulOutcome
# ============================================================

# Collect message types from BOTH the PR enum constants referenced in source
# AND direct PDU-level value.choice.X accesses (e.g.
# pdu->choice.initiatingMessage.value.choice.ResetRequest). Some messages are
# only accessed via value.choice without a corresponding PR constant reference,
# so scanning PR patterns alone misses them (e.g. ResetRequest).
init_msg_types = sorted(
    set(m.group(1) for m in re.finditer(r'X2AP_InitiatingMessage__value_PR_(\w+)', all_source)) |
    set(m.group(1) for m in re.finditer(r'choice\.initiatingMessage\.value\.choice\.(\w+)', all_source))
)
success_msg_types = sorted(
    set(m.group(1) for m in re.finditer(r'X2AP_SuccessfulOutcome__value_PR_(\w+)', all_source)) |
    set(m.group(1) for m in re.finditer(r'choice\.successfulOutcome\.value\.choice\.(\w+)', all_source))
)
unsuccess_msg_types = sorted(
    set(m.group(1) for m in re.finditer(r'X2AP_UnsuccessfulOutcome__value_PR_(\w+)', all_source)) |
    set(m.group(1) for m in re.finditer(r'choice\.unsuccessfulOutcome\.value\.choice\.(\w+)', all_source))
)

# ============================================================
# Scan generated X2AP_*.h headers for existing enum members.
# Any name that already exists as an enum member MUST NOT be re-#define'd,
# because the macro would expand the enum member name into a numeric
# constant at the enum declaration site ("expected identifier before numeric
# constant"). This happens when the generated header includes
# X2AP_oai_compat.h *before* declaring its own enum (e.g. X2AP_InitiatingMessage.h).
# ============================================================

existing_enum_members = set()
for hf in sorted(glob.glob(os.path.join(BUILD_DIR, "X2AP_*.h"))):
    if os.path.basename(hf) == "X2AP_oai_compat.h":
        continue
    try:
        htxt = open(hf).read()
    except OSError:
        continue
    # Match tagged and untagged enums: "enum TAG {" / "enum {".
    for m in re.finditer(r'enum\s*(?:\w+\s*)?\{([^}]*)\}', htxt, re.S):
        body = m.group(1)
        # Strip block comments so trailing members (often followed by a
        # "Extensions may appear below" comment with no comma) are caught.
        body = re.sub(r'/\*.*?\*/', ' ', body, flags=re.S)
        # Each comma-separated piece's first identifier is an enum member.
        # This also handles "NAME = value" and the last member (no comma).
        for piece in body.split(','):
            ids = re.findall(r'[A-Za-z_]\w*', piece)
            if ids:
                existing_enum_members.add(ids[0])

print(f"Existing enum members in generated headers: {len(existing_enum_members)}")

# ============================================================
# Find PR enum values needed
# ============================================================

pr_enums = set()
for m in re.finditer(r'X2AP_[A-Za-z0-9_]+_PR_[A-Za-z0-9_]+', all_source):
    pr_enums.add(m.group(0))

# Remove already-defined ones
for s in ['X2AP_X2AP_PDU_PR_NOTHING', 'X2AP_X2AP_PDU_PR_initiatingMessage',
          'X2AP_X2AP_PDU_PR_successfulOutcome', 'X2AP_X2AP_PDU_PR_unsuccessfulOutcome']:
    pr_enums.discard(s)

# Remove names already provided as enum members by generated headers
# (defining them as macros would collide with the enum declaration).
colliding_pr = sorted(pr_enums & existing_enum_members)
for c in colliding_pr:
    pr_enums.discard(c)
print(f"PR names skipped (already enum members): {len(colliding_pr)}")

# ============================================================
# Find Cause constants
# ============================================================

cause_constants = set()
for m in re.finditer(r'X2AP_Cause[A-Za-z0-9_]+', all_source):
    s = m.group(0)
    if s not in ('X2AP_Cause_PR', 'X2AP_Cause_PR_t', 'X2AP_Cause_t',
                 'X2AP_Cause_PR_misc', 'X2AP_Cause_PR_protocol',
                 'X2AP_Cause_PR_radioNetwork', 'X2AP_Cause_PR_transport'):
        cause_constants.add(s)

# Likewise drop Cause names already declared as enum members.
colliding_cause = sorted(cause_constants & existing_enum_members)
for c in colliding_cause:
    cause_constants.discard(c)
print(f"Cause names skipped (already enum members): {len(colliding_cause)}")

# ============================================================
# Determine C type for each choice member
# ============================================================

def get_c_type(name):
    """Get the C type declaration for a choice member."""
    if name in SIMPLE_TYPES and SIMPLE_TYPES[name] is not None:
        return SIMPLE_TYPES[name], True  # (type, is_simple)
    # Check if there's a generated header
    for hname in [f"X2AP_{name}.h", f"X2AP_{name.replace('_', '-')}.h"]:
        if os.path.exists(os.path.join(BUILD_DIR, hname)):
            return f"struct X2AP_{name}", False  # compound type
    # Default: assume it's a struct with generated header
    return f"struct X2AP_{name}", False

# ============================================================
# Generate X2AP_oai_compat.h
# ============================================================

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
#include "BIT_STRING.h"
#include "X2AP_ProcedureCode.h"
#include "X2AP_Criticality.h"
#include "X2AP_ProtocolIE-ID.h"
#include "X2AP_Cause.h"
#include "X2AP_TimeToWait.h"

/* Include generated type headers for compound types used in unions */
"""

# Collect needed includes for compound types
# Only truly primitive C types need no generated header; X2AP_*_t typedefs
# (enum/struct types listed in SIMPLE_TYPES) still require their header to be
# included, otherwise the union member's typedef is unknown.
PRIMITIVE_C_TYPES = {'long', 'OCTET_STRING_t', 'BIT_STRING_t'}
needed_includes = set()
for name in sorted(choice_members.keys()):
    if name in SIMPLE_TYPES and SIMPLE_TYPES[name] in PRIMITIVE_C_TYPES:
        continue  # primitive C type, no generated header needed
    if name in ('TimeToWait', 'InitiatingNodeType_EndcX2Setup', 'RespondingNodeType_EndcX2Setup',
                'ResponseInformationSgNBReconfComp', 'EUTRA_Mode_Info'):
        # These have their own headers - include them
        for hname in [f"X2AP_{name}.h", f"X2AP_{name.replace('_', '-')}.h"]:
            if os.path.exists(os.path.join(BUILD_DIR, hname)):
                needed_includes.add(hname)
                break
        continue
    # Try to find the header - try multiple naming patterns
    found = False
    for hname in [f"X2AP_{name}.h", f"X2AP_{name.replace('_', '-')}.h"]:
        if os.path.exists(os.path.join(BUILD_DIR, hname)):
            needed_includes.add(hname)
            found = True
            break
    if not found:
        # Some types like GlobalENB_ID have header as X2AP_GlobalENB-ID.h
        for f in os.listdir(BUILD_DIR):
            if f.startswith('X2AP_') and f.endswith('.h'):
                base = f[5:-2]  # Remove X2AP_ prefix and .h suffix
                if base.replace('-', '_') == name:
                    needed_includes.add(f)
                    break

for h in sorted(needed_includes):
    header += f'#include "{h}"\n'

# Include headers for OCTET_STRING/BIT_STRING container types whose _t typedef
# is used directly by OAI source (e.g. X2AP_MeNBtoSeNBContainer_t). These are
# listed in SIMPLE_TYPES as OCTET_STRING_t/BIT_STRING_t and thus were NOT added
# to needed_includes above (primitive C type), but the source declares variables
# of their _t typedef, so the generated header must be included.
CONTAINER_TYPES = [
    'MeNBtoSeNBContainer', 'MeNBtoSgNBContainer',
    'SeNBtoMeNBContainer', 'SgNBtoMeNBContainer',
    'TargeteNBtoSource-eNBTransparentContainer',
    'SourceeNBtoTargeteNBTransparentContainer',
    'SeNBSecurityKey', 'SgNBSecurityKey',
]
for cname in CONTAINER_TYPES:
    hname = f"X2AP_{cname}.h"
    if os.path.exists(os.path.join(BUILD_DIR, hname)):
        header += f'#include "{hname}"\n'

# Add PR enum defines
header += "\n/* ============================================================\n"
header += " * Missing PR enum values\n"
header += " * ============================================================ */\n\n"

pr_value = 0
for enum_name in sorted(pr_enums):
    if enum_name.endswith('_PR_t') or enum_name == 'X2AP_Cause_PR':
        continue
    header += f"#ifndef {enum_name}\n#define {enum_name} {pr_value}\n#endif\n"
    pr_value += 1

# Add Cause constants
header += "\n/* ============================================================\n"
header += " * Missing Cause constants\n"
header += " * ============================================================ */\n\n"

cause_vals = {
    'X2AP_CauseProtocol_unspecified': 0,
    'X2AP_CauseProtocol_transfer_syntax_error': 1,
    'X2AP_CauseProtocol_abstract_syntax_error_falsely_constructed_message': 2,
    'X2AP_CauseProtocol_abstract_syntax_error_unsupported': 3,
    'X2AP_CauseProtocol_abstract_syntax_error_reject': 4,
    'X2AP_CauseProtocol_abstract_syntax_error_ignore_and_notify': 5,
    'X2AP_CauseProtocol_message_not_compatible_with_receiver_state': 6,
    'X2AP_CauseMisc_unspecified': 0,
    'X2AP_CauseMisc_control_processing_overload': 1,
    'X2AP_CauseMisc_not_enough_user_plane_processing_resources': 2,
    'X2AP_CauseMisc_hardware_failure': 3,
    'X2AP_CauseMisc_om_intervention': 4,
    'X2AP_CauseMisc_unknown_PLMN': 5,
    'X2AP_CauseRadioNetwork_handover_desirable_for_radio_reasons': 0,
    'X2AP_CauseRadioNetwork_radio_connection_with_UE_lost': 1,
    'X2AP_CauseRadioNetwork_unspecified': 2,
    'X2AP_CauseRadioNetwork_trelocprep_expiry': 3,
    'X2AP_CauseRadioNetwork_tx2relocoverall_expiry': 4,
    'X2AP_CauseRadioNetwork_tDCprep_expiry': 5,
    'X2AP_CauseRadioNetwork_tDCoverall_expiry': 6,
    'X2AP_CauseRadioNetwork_x2_reset': 7,
}

for name in sorted(cause_constants):
    val = cause_vals.get(name, 0)
    header += f"#ifndef {name}\n#define {name} {val}\n#endif\n"

# ============================================================
# Map OAI's X2AP_-prefixed enum constant names to the generated (unprefixed)
# enum members. This asn1c version emits value-enum members WITHOUT the X2AP_
# prefix (e.g. Criticality_reject, Transmission_Bandwidth_bw6), while OAI source
# references the prefixed form (X2AP_Criticality_reject). For each generated
# enum member M that lacks the prefix, if the source references X2AP_M and that
# prefixed name is not itself an enum member, define X2AP_M -> M.
# ============================================================

header += "\n/* ============================================================\n"
header += " * X2AP_-prefixed enum constant aliases (generated members are unprefixed)\n"
header += " * ============================================================ */\n\n"

enum_alias_count = 0
for member in sorted(existing_enum_members):
    if member.startswith("X2AP_"):
        continue  # already prefixed (e.g. PR enums)
    prefixed = "X2AP_" + member
    if prefixed in existing_enum_members:
        continue  # would collide with a real enum member
    # Whole-word search in OAI source for the prefixed reference
    if re.search(r'\b' + re.escape(prefixed) + r'\b', all_source):
        header += f"#ifndef {prefixed}\n#define {prefixed} {member}\n#endif\n"
        enum_alias_count += 1
print(f"Enum alias #defines (X2AP_-prefixed -> unprefixed): {enum_alias_count}")

# Add ServedCells__Member type and the related NR/EUTRA list member typedefs.
# OAI source uses the unprefixed names (ServedCells__Member,
# ServedNRcellsENDCX2ManagementList__Member, ServedEUTRAcellsENDCX2ManagementList__Member)
# while the generated asn1c code defines them as inline structs with an X2AP_ prefix
# (struct X2AP_ServedCells__Member inside A_SEQUENCE_OF). Provide typedefs so the
# unprefixed names resolve to the same type.
header += """
/* ============================================================
 * ServedCells__Member and related list member typedefs
 * ============================================================ */

#include "X2AP_ServedCells.h"
#include "X2AP_ServedNRcellsENDCX2ManagementList.h"
#include "X2AP_ServedEUTRAcellsENDCX2ManagementList.h"

typedef struct X2AP_ServedCells__Member ServedCells__Member;
typedef struct X2AP_ServedNRcellsENDCX2ManagementList__Member ServedNRcellsENDCX2ManagementList__Member;
typedef struct X2AP_ServedEUTRAcellsENDCX2ManagementList__Member ServedEUTRAcellsENDCX2ManagementList__Member;

"""

# Build the IE value union
header += "/* ============================================================\n"
header += " * IE value union - OAI accesses value.choice.X\n"
header += " * ============================================================ */\n\n"

header += "typedef struct X2AP_IE_Value {\n"
header += "    long present;  /* discriminator */\n"
header += "    union X2AP_IE_Value_u {\n"
header += "        void *ptr;\n\n"

for name in sorted(choice_members.keys()):
    kind = choice_members[name]
    c_type, is_simple = get_c_type(name)

    if kind == 'pointer':
        # Pointer member: struct X2AP_X *X;
        if is_simple:
            header += f"        {c_type} *{name};\n"
        else:
            header += f"        {c_type} *{name};\n"
    else:
        # Embedded value member
        if is_simple:
            header += f"        {c_type} {name};\n"
        else:
            # For compound types, use the typedef name (e.g., X2AP_Cause_t)
            # The header must be included above for the typedef to be visible
            header += f"        X2AP_{name}_t {name};\n"

header += "    } choice;\n"
header += "} X2AP_IE_Value_t;\n\n"

# Define struct X2AP_ProtocolIE_Field
header += "/* ============================================================\n"
header += " * struct X2AP_ProtocolIE_Field - complete definition\n"
header += " * The generated containers use A_SEQUENCE_OF(struct X2AP_ProtocolIE_Field)\n"
header += " * ============================================================ */\n\n"

header += "struct X2AP_ProtocolIE_Field {\n"
header += "    X2AP_ProtocolIE_ID_t     id;\n"
header += "    X2AP_Criticality_t       criticality;\n"
header += "    X2AP_IE_Value_t  value;\n"
header += "    asn_struct_ctx_t _asn_ctx;\n"
header += "};\n"
header += "typedef struct X2AP_ProtocolIE_Field X2AP_ProtocolIE_Field_t;\n\n"

# Typedef all IEs_t types
for t in sorted(ies_types):
    header += f"typedef X2AP_ProtocolIE_Field_t {t};\n"

# Add macros
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

#endif /* X2AP_OAI_COMPAT_H */
"""

with open(COMPAT_HEADER, 'w') as f:
    f.write(header)
print(f"Generated {COMPAT_HEADER} ({len(header)} bytes)")

# ============================================================
# Modify X2AP_InitiatingMessage.h
# ============================================================

def get_msg_union_member(t, source):
    """Get union member declaration for a message type."""
    # Check if source accesses this with -> (pointer) or . (value)
    if re.search(rf'value\.choice\.{re.escape(t)}\s*->', source):
        return f"\t\tX2AP_{t}_t\t *{t};\n"
    else:
        # Check if it's a simple type
        if t in SIMPLE_TYPES and SIMPLE_TYPES[t] is not None:
            return f"\t\t{SIMPLE_TYPES[t]}\t {t};\n"
        # Use the typedef name (e.g., X2AP_X2SetupRequest_t)
        return f"\t\tX2AP_{t}_t\t {t};\n"

init_header_path = os.path.join(BUILD_DIR, "X2AP_InitiatingMessage.h")
fwd_decls = "\n".join(f"struct X2AP_{t};" for t in init_msg_types)
union_members = "".join(get_msg_union_member(t, all_source) for t in init_msg_types)

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
{union_members}\t}} choice;
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

for t in init_msg_types:
    init_content += f"\tX2AP_InitiatingMessage__value_PR_{t},\n"

init_content += """} X2AP_InitiatingMessage__value_PR_t;

extern asn_TYPE_descriptor_t asn_DEF_X2AP_InitiatingMessage;

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
# Modify X2AP_SuccessfulOutcome.h
# ============================================================

success_header_path = os.path.join(BUILD_DIR, "X2AP_SuccessfulOutcome.h")
fwd_decls_s = "\n".join(f"struct X2AP_{t};" for t in success_msg_types)
union_members_s = "".join(get_msg_union_member(t, all_source) for t in success_msg_types)

success_content = f"""/*
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

typedef struct X2AP_SuccessfulOutcome_value {{
\tlong present;
\tunion X2AP_SuccessfulOutcome_value_u {{
{union_members_s}\t}} choice;
\tasn_struct_ctx_t _asn_ctx;
}} X2AP_SuccessfulOutcome_value_t;

typedef struct X2AP_SuccessfulOutcome {{
\tX2AP_ProcedureCode_t\t procedureCode;
\tX2AP_Criticality_t\t criticality;
\tX2AP_SuccessfulOutcome_value_t\t value;
\tasn_struct_ctx_t _asn_ctx;
}} X2AP_SuccessfulOutcome_t;

typedef enum X2AP_SuccessfulOutcome__value_PR {{
\tX2AP_SuccessfulOutcome__value_PR_NOTHING,
"""

for t in success_msg_types:
    success_content += f"\tX2AP_SuccessfulOutcome__value_PR_{t},\n"

success_content += """} X2AP_SuccessfulOutcome__value_PR_t;

extern asn_TYPE_descriptor_t asn_DEF_X2AP_SuccessfulOutcome;

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
# Modify X2AP_UnsuccessfulOutcome.h
# ============================================================

unsuccess_header_path = os.path.join(BUILD_DIR, "X2AP_UnsuccessfulOutcome.h")
fwd_decls_u = "\n".join(f"struct X2AP_{t};" for t in unsuccess_msg_types)
union_members_u = "".join(get_msg_union_member(t, all_source) for t in unsuccess_msg_types)

unsuccess_content = f"""/*
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

typedef struct X2AP_UnsuccessfulOutcome_value {{
\tlong present;
\tunion X2AP_UnsuccessfulOutcome_value_u {{
{union_members_u}\t}} choice;
\tasn_struct_ctx_t _asn_ctx;
}} X2AP_UnsuccessfulOutcome_value_t;

typedef struct X2AP_UnsuccessfulOutcome {{
\tX2AP_ProcedureCode_t\t procedureCode;
\tX2AP_Criticality_t\t criticality;
\tX2AP_UnsuccessfulOutcome_value_t\t value;
\tasn_struct_ctx_t _asn_ctx;
}} X2AP_UnsuccessfulOutcome_t;

typedef enum X2AP_UnsuccessfulOutcome__value_PR {{
\tX2AP_UnsuccessfulOutcome__value_PR_NOTHING,
"""

for t in unsuccess_msg_types:
    unsuccess_content += f"\tX2AP_UnsuccessfulOutcome__value_PR_{t},\n"

unsuccess_content += """} X2AP_UnsuccessfulOutcome__value_PR_t;

extern asn_TYPE_descriptor_t asn_DEF_X2AP_UnsuccessfulOutcome;

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
# Ensure x2ap_common.h includes compat header
# ============================================================

common_header_path = os.path.join(SRC_DIR, "x2ap_common.h")
with open(common_header_path) as f:
    common_content = f.read()

if 'X2AP_oai_compat.h' not in common_content:
    common_content = common_content.replace(
        '#include "X2AP_Cause.h"',
        '#include "X2AP_Cause.h"\n#include "X2AP_oai_compat.h"'
    )
    with open(common_header_path, 'w') as f:
        f.write(common_content)
    print(f"Modified {common_header_path}")

print("\n=== X2AP compat generation v2 complete ===")
