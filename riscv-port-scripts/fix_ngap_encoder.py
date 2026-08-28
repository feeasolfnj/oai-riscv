#!/usr/bin/env python3
"""Fix ngap_gNB_nas_procedures.c: replace asn_encode_to_new_buffer with
aper_encode_to_new_buffer, and add missing PR constant to compat header."""
import re

NAS_FILE = "/home/kongbai/openairinterface5g/openair3/NGAP/ngap_gNB_nas_procedures.c"
COMPAT_H = "/home/kongbai/openairinterface5g/build-riscv/openair3/NGAP/MESSAGES/NGAP_oai_compat.h"

with open(NAS_FILE, 'r') as f:
    src = f.read()

# Pattern 1 & 2: declaration + AssertFatal + 2 assignments
# asn_encode_to_new_buffer_result_t res = asn_encode_to_new_buffer(NULL, ATS_ALIGNED_CANONICAL_PER, &asn_DEF_X, &data);
# AssertFatal(res.buffer, "...", res.result.failed_type->name, res.result.encoded);
# item->field.buf = res.buffer;
# item->field.size = res.result.encoded;
pat1 = re.compile(
    r'asn_encode_to_new_buffer_result_t res = asn_encode_to_new_buffer\(NULL, ATS_ALIGNED_CANONICAL_PER, (&asn_DEF_\w+), (&\w+)\);\n'
    r'\s*AssertFatal\s*\(\s*res\.buffer.*?res\.result\.encoded\s*\);\n'
    r'\s*(\w+)->(\w+\.buf)\s*=\s*res\.buffer;\n'
    r'\s*\3->\s*\4\.size\s*=\s*res\.result\.encoded;'
)
def rep1(m):
    defref, dataref, item, field = m.group(1), m.group(2), m.group(3), m.group(4)
    return (
        f'void *encode_buffer = NULL;\n'
        f'      ssize_t encoded_len = aper_encode_to_new_buffer({defref}, NULL, {dataref}, &encode_buffer);\n'
        f'      AssertFatal(encode_buffer && encoded_len > 0, "ASN1 message encoding failed!\\n");\n'
        f'      {item}->{field} = encode_buffer;\n'
        f'      {item}->{field.replace(".buf", ".size")} = encoded_len;'
    )
src, n1 = pat1.subn(rep1, src)
print(f"Pattern 1 (AssertFatal): {n1} replacements")

# Pattern 3: declaration + 2 assignments (no AssertFatal)
# asn_encode_to_new_buffer_result_t res = asn_encode_to_new_buffer(NULL, ATS_ALIGNED_CANONICAL_PER, &asn_DEF_X, &data);
# item->field.buf = res.buffer;
# item->field.size = res.result.encoded;
pat3 = re.compile(
    r'asn_encode_to_new_buffer_result_t res = asn_encode_to_new_buffer\(NULL, ATS_ALIGNED_CANONICAL_PER, (&asn_DEF_\w+), (&\w+)\);\n'
    r'\s*(\w+)->(\w+)\.buf\s*=\s*res\.buffer;\n'
    r'\s*\3->\s*\4\.size\s*=\s*res\.result\.encoded;'
)
def rep3(m):
    defref, dataref, item, field = m.group(1), m.group(2), m.group(3), m.group(4)
    return (
        f'void *encode_buffer = NULL;\n'
        f'      ssize_t encoded_len = aper_encode_to_new_buffer({defref}, NULL, {dataref}, &encode_buffer);\n'
        f'      {item}->{field}.buf = encode_buffer;\n'
        f'      {item}->{field}.size = encoded_len;'
    )
src, n3 = pat3.subn(rep3, src)
print(f"Pattern 3 (no assert): {n3} replacements")

# Pattern 4 & 5: split declaration and assignment
# asn_encode_to_new_buffer_result_t res = {0};
# ... (some lines) ...
# res = asn_encode_to_new_buffer(NULL, ATS_ALIGNED_CANONICAL_PER, &asn_DEF_X, data);
# item->field.buf = res.buffer;
# item->field.size = res.result.encoded;
pat4_decl = re.compile(r'asn_encode_to_new_buffer_result_t res = \{0\};')
src, n4d = pat4_decl.subn('void *encode_buffer = NULL;\n      ssize_t encoded_len = 0;', src)
print(f"Pattern 4 (decl): {n4d} replacements")

pat4_call = re.compile(
    r'res = asn_encode_to_new_buffer\(NULL, ATS_ALIGNED_CANONICAL_PER, (&asn_DEF_\w+), (\w+)\);\n'
    r'\s*(\w+)->(\w+Transfer)\.buf\s*=\s*res\.buffer;\n'
    r'\s*\3->\s*\4Transfer\.size\s*=\s*res\.result\.encoded;'
)
def rep4(m):
    defref, dataref, item, field = m.group(1), m.group(2), m.group(3), m.group(4)
    return (
        f'encoded_len = aper_encode_to_new_buffer({defref}, NULL, {dataref}, &encode_buffer);\n'
        f'      {item}->{field}.buf = encode_buffer;\n'
        f'      {item}->{field}.size = encoded_len;'
    )
src, n4c = pat4_call.subn(rep4, src)
print(f"Pattern 4 (call): {n4c} replacements")

# Add per_encoder.h include if not present
if 'per_encoder.h' not in src:
    # Add after ngap_gNB_nas_procedures.h include
    src = re.sub(
        r'(#include "ngap_gNB_nas_procedures\.h")',
        r'\1\n#include "per_encoder.h"',
        src
    )
    print("Added per_encoder.h include")

with open(NAS_FILE, 'w') as f:
    f.write(src)

# Verify no remaining old API
remaining = src.count('asn_encode_to_new_buffer')
print(f"Remaining 'asn_encode_to_new_buffer' occurrences: {remaining}")

# === Add missing PR constant to compat header ===
with open(COMPAT_H, 'r') as f:
    compat = f.read()

if 'NGAP_PDUSessionResourceSetupResponseIEs__value_PR_CriticalityDiagnostics' not in compat:
    # Add after the existing PDUSessionResourceSetupResponseIEs defines
    compat = compat.replace(
        '#define NGAP_PDUSessionResourceSetupResponseIEs__value_PR_PDUSessionResourceFailedToSetupListSURes 3',
        '#define NGAP_PDUSessionResourceSetupResponseIEs__value_PR_PDUSessionResourceFailedToSetupListSURes 3\n'
        '#define NGAP_PDUSessionResourceSetupResponseIEs__value_PR_CriticalityDiagnostics 4'
    )
    with open(COMPAT_H, 'w') as f:
        f.write(compat)
    print("Added NGAP_PDUSessionResourceSetupResponseIEs__value_PR_CriticalityDiagnostics")
else:
    print("PR constant already exists")

print("\nDone!")
