#!/usr/bin/env python3
"""Fix cast type names in nr_mac_common.c - use _t suffix for typedef names."""

filepath = "/home/kongbai/openairinterface5g/openair2/LAYER2/NR_MAC_COMMON/nr_mac_common.c"

with open(filepath, 'r') as f:
    content = f.read()

fixes = []

# Fix: NR_PUSCH_CodeBlockGroupTransmission -> NR_PUSCH_CodeBlockGroupTransmission_t
old = '((NR_PUSCH_CodeBlockGroupTransmission*)'
new = '((NR_PUSCH_CodeBlockGroupTransmission_t*)'
if old in content:
    content = content.replace(old, new)
    fixes.append(f"Fixed cast: {old} -> {new}")

# Fix: NR_PDSCH_CodeBlockGroupTransmission -> NR_PDSCH_CodeBlockGroupTransmission_t
old = '((NR_PDSCH_CodeBlockGroupTransmission*)'
new = '((NR_PDSCH_CodeBlockGroupTransmission_t*)'
if old in content:
    content = content.replace(old, new)
    fixes.append(f"Fixed cast: {old} -> {new}")

# Fix: NR_UCI_OnPUSCH -> NR_UCI_OnPUSCH_t
old = '((NR_UCI_OnPUSCH*)'
new = '((NR_UCI_OnPUSCH_t*)'
if old in content:
    content = content.replace(old, new)
    fixes.append(f"Fixed cast: {old} -> {new}")

with open(filepath, 'w') as f:
    f.write(content)

for fix in fixes:
    print(fix)

print(f"\nTotal fixes: {len(fixes)}")
