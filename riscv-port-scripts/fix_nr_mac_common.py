#!/usr/bin/env python3
"""Fix compilation errors in nr_mac_common.c for RISC-V cross-compilation."""

import re

filepath = "/home/kongbai/openairinterface5g/openair2/LAYER2/NR_MAC_COMMON/nr_mac_common.c"

with open(filepath, 'r') as f:
    content = f.read()

fixes = []

# Fix 1: Line 3006 - typo: pusch_Configpusch_Config -> pusch_Config
old = 'pusch_Configpusch_Config->ul_FullPowerTransmission_r16'
new = 'pusch_Config->ul_FullPowerTransmission_r16'
if old in content:
    content = content.replace(old, new)
    fixes.append(f"Fix 1: Fixed typo '{old}' -> '{new}'")

# Fix 2: Line 3429 - codeBlockGroupTransmission->choice.setup-> for PUSCH
# UL_BWP->pusch_servingcellconfig->codeBlockGroupTransmission->choice.setup->maxCodeBlockGroupsPerTransportBlock
old = 'UL_BWP->pusch_servingcellconfig->codeBlockGroupTransmission->choice.setup->maxCodeBlockGroupsPerTransportBlock'
new = '((NR_PUSCH_CodeBlockGroupTransmission*)UL_BWP->pusch_servingcellconfig->codeBlockGroupTransmission->choice.setup)->maxCodeBlockGroupsPerTransportBlock'
if old in content:
    content = content.replace(old, new)
    fixes.append(f"Fix 2: Cast PUSCH codeBlockGroupTransmission to correct type")

# Fix 3: Line 3447 - uci_OnPUSCH->choice.setup->betaOffsets
old = 'pusch_Config->uci_OnPUSCH->choice.setup->betaOffsets'
new = '((NR_UCI_OnPUSCH*)pusch_Config->uci_OnPUSCH->choice.setup)->betaOffsets'
if old in content:
    content = content.replace(old, new)
    fixes.append(f"Fix 3: Cast uci_OnPUSCH to correct type")

# Fix 4: Line 3581 - PDSCH codeBlockGroupTransmission maxCodeBlockGroupsPerTransportBlock
old = 'DL_BWP->pdsch_servingcellconfig->codeBlockGroupTransmission->choice.setup->maxCodeBlockGroupsPerTransportBlock'
new = '((NR_PDSCH_CodeBlockGroupTransmission*)DL_BWP->pdsch_servingcellconfig->codeBlockGroupTransmission->choice.setup)->maxCodeBlockGroupsPerTransportBlock'
if old in content:
    content = content.replace(old, new)
    fixes.append(f"Fix 4: Cast PDSCH codeBlockGroupTransmission to correct type (maxCodeBlockGroupsPerTransportBlock)")

# Fix 5: Line 3587 - PDSCH codeBlockGroupTransmission codeBlockGroupFlushIndicator
old = 'DL_BWP->pdsch_servingcellconfig->codeBlockGroupTransmission->choice.setup->codeBlockGroupFlushIndicator'
new = '((NR_PDSCH_CodeBlockGroupTransmission*)DL_BWP->pdsch_servingcellconfig->codeBlockGroupTransmission->choice.setup)->codeBlockGroupFlushIndicator'
if old in content:
    content = content.replace(old, new)
    fixes.append(f"Fix 5: Cast PDSCH codeBlockGroupTransmission to correct type (codeBlockGroupFlushIndicator)")

# Fix 6: Lines 3643-3644 and 3677-3678 - pattern1.ext1 -> pattern1 (remove ext1)
old = 'tdd_UL_DL_ConfigurationCommon->pattern1.ext1'
new = 'tdd_UL_DL_ConfigurationCommon->pattern1.dl_UL_TransmissionPeriodicity_v1530'
if old in content:
    content = content.replace(old, new)
    fixes.append(f"Fix 6: Removed ext1 from pattern1 access")

# Fix 7: Lines 3650 and 3684 - pattern2tdd_UL_DL_ConfigurationCommon->pattern2 -> pattern2
old = 'tdd_UL_DL_ConfigurationCommon->pattern2tdd_UL_DL_ConfigurationCommon->pattern2->'
new = 'tdd_UL_DL_ConfigurationCommon->pattern2->'
if old in content:
    content = content.replace(old, new)
    fixes.append(f"Fix 7: Fixed pattern2 typo")

with open(filepath, 'w') as f:
    f.write(content)

for fix in fixes:
    print(fix)

print(f"\nTotal fixes applied: {len(fixes)}")
