#!/usr/bin/env python3
"""Comprehensive fix for all NGAP header issues."""

import os
import re

GEN_DIR = "/home/kongbai/openairinterface5g/build-riscv/openair3/NGAP/MESSAGES"

# ============= 1. Fix NGAP_InitiatingMessage.h =============
init_msg_h = os.path.join(GEN_DIR, "NGAP_InitiatingMessage.h")

# All message types accessed in InitiatingMessage union
init_msg_types = [
    "NGSetupRequest",
    "InitialContextSetupRequest",
    "UEContextReleaseCommand",
    "UEContextReleaseRequest",
    "PDUSessionResourceSetupRequest",
    "PDUSessionResourceModifyRequest",
    "PDUSessionResourceReleaseCommand",
    "ErrorIndication",
    "DownlinkNASTransport",
    "InitialUEMessage",
    "UplinkNASTransport",
    "NASNonDeliveryIndication",
    "Paging",
    "PathSwitchRequest",
    "UERadioCapabilityInfoIndication",
    "OverloadStart",
    "OverloadStop",
]

with open(init_msg_h, 'r') as f:
    content = f.read()

# Replace forward declarations
old_fwd = "/* Forward declarations for message types */\nstruct NGAP_NGSetupRequest;"
new_fwd = "/* Forward declarations for message types */\n" + \
          "\n".join(f"struct NGAP_{t};" for t in init_msg_types)

content = content.replace(
    old_fwd + "\n" + "\n".join(f"struct NGAP_{t};" for t in init_msg_types if t != "NGSetupRequest"),
    new_fwd
)

# Actually, let's just replace everything between the forward declarations comment and the value typedef
# Find the block and replace it
content = re.sub(
    r'/\* Forward declarations for message types \*/\n.*?/\* NGAP_InitiatingMessage value \*/',
    '/* Forward declarations for message types */\n' + 
    "\n".join(f"struct NGAP_{t};" for t in init_msg_types) + 
    '\n\n/* NGAP_InitiatingMessage value */',
    content,
    flags=re.DOTALL
)

# Replace the union body
old_union_start = "	union NGAP_InitiatingMessage_value_u {"
new_union = "	union NGAP_InitiatingMessage_value_u {\n" + \
    "\n".join(f"		struct NGAP_{t}	*{t};" for t in init_msg_types) + \
    "\n		/* Extensions may appear below */"

content = re.sub(
    r'union NGAP_InitiatingMessage_value_u \{.*?\} choice;',
    new_union + "\n	} choice;",
    content,
    flags=re.DOTALL
)

with open(init_msg_h, 'w') as f:
    f.write(content)
print("Fixed NGAP_InitiatingMessage.h")

# ============= 2. Fix NGAP_SuccessfulOutcome.h =============
succ_msg_h = os.path.join(GEN_DIR, "NGAP_SuccessfulOutcome.h")

succ_msg_types = [
    "NGSetupResponse",
    "InitialContextSetupResponse",
    "UEContextReleaseComplete",
    "PDUSessionResourceSetupResponse",
    "PDUSessionResourceModifyResponse",
    "PDUSessionResourceReleaseResponse",
]

with open(succ_msg_h, 'r') as f:
    content = f.read()

content = re.sub(
    r'/\* Forward declarations for message types \*/\n.*?/\* NGAP_SuccessfulOutcome value \*/',
    '/* Forward declarations for message types */\n' + 
    "\n".join(f"struct NGAP_{t};" for t in succ_msg_types) + 
    '\n\n/* NGAP_SuccessfulOutcome value */',
    content,
    flags=re.DOTALL
)

content = re.sub(
    r'union NGAP_SuccessfulOutcome_value_u \{.*?\} choice;',
    "union NGAP_SuccessfulOutcome_value_u {\n" + 
    "\n".join(f"		struct NGAP_{t}	*{t};" for t in succ_msg_types) + 
    "\n		/* Extensions may appear below */\n	} choice;",
    content,
    flags=re.DOTALL
)

with open(succ_msg_h, 'w') as f:
    f.write(content)
print("Fixed NGAP_SuccessfulOutcome.h")

# ============= 3. Fix NGAP_UnsuccessfulOutcome.h =============
unsucc_msg_h = os.path.join(GEN_DIR, "NGAP_UnsuccessfulOutcome.h")

unsucc_msg_types = [
    "NGSetupFailure",
    "InitialContextSetupFailure",
]

with open(unsucc_msg_h, 'r') as f:
    content = f.read()

content = re.sub(
    r'/\* Forward declarations for message types \*/\n.*?/\* NGAP_UnsuccessfulOutcome value \*/',
    '/* Forward declarations for message types */\n' + 
    "\n".join(f"struct NGAP_{t};" for t in unsucc_msg_types) + 
    '\n\n/* NGAP_UnsuccessfulOutcome value */',
    content,
    flags=re.DOTALL
)

content = re.sub(
    r'union NGAP_UnsuccessfulOutcome_value_u \{.*?\} choice;',
    "union NGAP_UnsuccessfulOutcome_value_u {\n" + 
    "\n".join(f"		struct NGAP_{t}	*{t};" for t in unsucc_msg_types) + 
    "\n		/* Extensions may appear below */\n	} choice;",
    content,
    flags=re.DOTALL
)

with open(unsucc_msg_h, 'w') as f:
    f.write(content)
print("Fixed NGAP_UnsuccessfulOutcome.h")

# ============= 4. Fix NGAP_oai_compat.h - add missing symbols =============
compat_h = os.path.join(GEN_DIR, "NGAP_oai_compat.h")

with open(compat_h, 'r') as f:
    content = f.read()

# Add missing ProcedureCode IDs
missing_proc_codes = {
    "id_UEContextReleaseRequest": 42,
}
for name, value in missing_proc_codes.items():
    macro = f"#define NGAP_ProcedureCode_{name} {value}"
    if macro not in content:
        content = content.replace(
            "/* NGAP ProtocolIE-ID constants */",
            f"{macro}\n/* NGAP ProtocolIE-ID constants */"
        )

# Add missing InitiatingMessage PR values
missing_init_prs = {
    "NGAP_InitiatingMessage__value_PR_UEContextReleaseRequest": 19,
}
for name, value in missing_init_prs.items():
    macro = f"#define {name} {value}"
    if macro not in content:
        content = content.replace(
            "/* SuccessfulOutcome value PR enum values */",
            f"{macro}\n/* SuccessfulOutcome value PR enum values */"
        )

# Add missing IE typedefs
missing_ie_typedefs = [
    "NGAP_UEContextReleaseRequest_IEs_t",
    "NGAP_DeactivateTraceIEs_t",
]
for typedef in missing_ie_typedefs:
    typedef_line = f"typedef NGAP_Message_IEs_t {typedef};"
    if typedef_line not in content:
        # Add after the last typedef
        content = content.replace(
            "typedef NGAP_Message_IEs_t NGAP_PDUSessionResourceNotifyIEs_t;",
            f"typedef NGAP_Message_IEs_t NGAP_PDUSessionResourceNotifyIEs_t;\ntypedef NGAP_Message_IEs_t {typedef};"
        )

# Add missing NGAP_UEContextReleaseRequest_t typedef (it should come from generated header)
# Check if the generated header exists
ue_ctx_rel_req_h = os.path.join(GEN_DIR, "NGAP_UEContextReleaseRequest.h")
if os.path.exists(ue_ctx_rel_req_h):
    # Make sure it's included
    if '#include "NGAP_UEContextReleaseRequest.h"' not in content:
        content = content.replace(
            '#include "NGAP_NGSetupRequest.h"',
            '#include "NGAP_UEContextReleaseRequest.h"\n#include "NGAP_NGSetupRequest.h"'
        )

with open(compat_h, 'w') as f:
    f.write(content)
print("Fixed NGAP_oai_compat.h")

print("\nDone! All NGAP headers updated.")
