#!/usr/bin/env python3
"""Extract ProcedureCode and ProtocolIE-ID constants from X2AP ASN.1 source
and add them to X2AP_asn_constant.h. The asn1c-oai wrapper only extracts
INTEGER constants, missing ProcedureCode/ProtocolIE-ID typed constants."""
import re
import os

ASN1_FILE = "/home/kongbai/openairinterface5g/openair2/X2AP/MESSAGES/ASN1/R15/x2ap-15.6.0.asn1"
CONST_H = "/home/kongbai/openairinterface5g/build-riscv/openair2/X2AP/MESSAGES/X2AP_asn_constant.h"

with open(ASN1_FILE, 'r') as f:
    asn1_content = f.read()

# Extract all constants of various types
# Pattern: name TypeName ::= value
# Types we care about: ProcedureCode, ProtocolIE-ID, Criticality, TriggeringMessage
type_pattern = re.compile(
    r'^(\s*)(id-[A-Za-z0-9_-]+)\s+(ProcedureCode|ProtocolIE-ID|Criticality|TriggeringMessage)\s*::=\s*(\d+)',
    re.MULTILINE
)

constants = {}
for m in type_pattern.finditer(asn1_content):
    name = m.group(2)  # e.g., id-x2Setup
    type_name = m.group(3)  # e.g., ProcedureCode
    value = m.group(4)  # e.g., 6

    # Convert to C name: X2AP_ + TypeName (hyphens to underscores) + _ + name (hyphens to underscores)
    c_type = type_name.replace('-', '_')
    c_name = name.replace('-', '_')
    c_full = f"X2AP_{c_type}_{c_name}"

    constants[c_full] = value

print(f"Extracted {len(constants)} constants")

# Read existing constant header
with open(CONST_H, 'r') as f:
    content = f.read()

# Find what's already defined to avoid duplicates
existing = set(re.findall(r'#define\s+(\w+)', content))
new_constants = {k: v for k, v in constants.items() if k not in existing}
print(f"New constants to add: {len(new_constants)}")

if new_constants:
    # Generate the new defines
    lines = []
    for name in sorted(new_constants.keys()):
        lines.append(f"#define {name} {new_constants[name]}")

    block = "\n/* ProcedureCode and ProtocolIE-ID constants */\n" + "\n".join(lines) + "\n"

    # Insert before the #ifdef __cplusplus closing
    content = content.replace(
        '#ifdef __cplusplus\n}\n#endif',
        block + '\n#ifdef __cplusplus\n}\n#endif'
    )

    with open(CONST_H, 'w') as f:
        f.write(content)
    print(f"Added {len(new_constants)} constants to {CONST_H}")
else:
    print("No new constants to add")

# Verify the OAI-referenced constants are now defined
oai_refs = [
    "X2AP_ProcedureCode_id_endcX2Setup", "X2AP_ProcedureCode_id_handoverCancel",
    "X2AP_ProcedureCode_id_handoverPreparation", "X2AP_ProcedureCode_id_meNBinitiatedSgNBRelease",
    "X2AP_ProcedureCode_id_seNBAdditionPreparation", "X2AP_ProcedureCode_id_sgNBAdditionPreparation",
    "X2AP_ProcedureCode_id_sgNBReconfigurationCompletion", "X2AP_ProcedureCode_id_sgNBinitiatedSgNBRelease",
    "X2AP_ProcedureCode_id_uEContextRelease", "X2AP_ProcedureCode_id_x2Setup",
]
print("\nVerification:")
for ref in oai_refs:
    with open(CONST_H, 'r') as f:
        c = f.read()
    status = "OK" if f"#define {ref}" in c else "MISSING"
    print(f"  {ref}: {status}")
