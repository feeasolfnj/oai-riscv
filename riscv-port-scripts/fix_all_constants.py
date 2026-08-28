#!/usr/bin/env python3
"""Extract ProcedureCode, ProtocolIE-ID, Criticality, TriggeringMessage constants
from ASN.1 source files for S1AP, F1AP, E1AP and add to their asn_constant.h files.
The asn1c-oai wrapper only extracts INTEGER constants, missing these typed constants."""
import re
import os
import glob

MODULES = [
    ("S1AP", "/home/kongbai/openairinterface5g/openair3/S1AP/MESSAGES"),
    ("F1AP", "/home/kongbai/openairinterface5g/openair2/F1AP/MESSAGES"),
    ("E1AP", "/home/kongbai/openairinterface5g/openair2/E1AP/MESSAGES"),
]

type_pattern = re.compile(
    r'^(\s*)(id-[A-Za-z0-9_-]+)\s+(ProcedureCode|ProtocolIE-ID|Criticality|TriggeringMessage)\s*::=\s*(\d+)',
    re.MULTILINE
)

for prefix, msg_dir in MODULES:
    build_msg_dir = msg_dir.replace("/openairinterface5g/openair", "/openairinterface5g/build-riscv/openair")
    const_h = os.path.join(build_msg_dir, f"{prefix}_asn_constant.h")

    # Find ASN.1 source files
    asn1_files = glob.glob(os.path.join(msg_dir, "ASN1", "*.asn1")) + \
                 glob.glob(os.path.join(msg_dir, "ASN1", "**", "*.asn1"), recursive=True)

    if not os.path.exists(const_h):
        print(f"{prefix}: constant header not found at {const_h}")
        continue

    # Extract constants from all ASN.1 files
    constants = {}
    for asn1_file in asn1_files:
        with open(asn1_file, 'r', errors='replace') as f:
            content = f.read()
        for m in type_pattern.finditer(content):
            name = m.group(2)
            type_name = m.group(3)
            value = m.group(4)
            c_type = type_name.replace('-', '_')
            c_name = name.replace('-', '_')
            c_full = f"{prefix}_{c_type}_{c_name}"
            constants[c_full] = value

    # Read existing constant header
    with open(const_h, 'r') as f:
        header_content = f.read()

    existing = set(re.findall(r'#define\s+(\w+)', header_content))
    new_constants = {k: v for k, v in constants.items() if k not in existing}

    if new_constants:
        lines = []
        for name in sorted(new_constants.keys()):
            lines.append(f"#define {name} {new_constants[name]}")
        block = "\n/* ProcedureCode and ProtocolIE-ID constants */\n" + "\n".join(lines) + "\n"
        header_content = header_content.replace(
            '#ifdef __cplusplus\n}\n#endif',
            block + '\n#ifdef __cplusplus\n}\n#endif'
        )
        with open(const_h, 'w') as f:
            f.write(header_content)
        print(f"{prefix}: added {len(new_constants)} constants")
    else:
        print(f"{prefix}: no new constants needed")

print("\nDone!")
