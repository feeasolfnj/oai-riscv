#!/usr/bin/env python3
"""
fix_ngap_compat.py --dir DIR

NGAP_oai_compat.h is a hand-made patch header (from the 844f9ca era) that
#defines ASN.1 enum/const values that 844f9ca failed to emit.  With
asn1c-940dd5fa most of those values ARE emitted (as #define or enum members),
so the compat #defines now collide with the generated ones:

  * #define vs enum member  -> compile error (identifier replaced by number)
  * #define vs #define      -> benign redefinition, still drop it

Keep only the compat #defines whose name is NOT defined anywhere else in the
generated headers.  Idempotent.
"""

import argparse
import os
import re
import sys

DEFINE_RE = re.compile(r'^#define\s+(\w+)')
ENUM_MEMBER_RE = re.compile(r'^\s{1,2}([A-Za-z_]\w*),?\s*$')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dir', required=True)
    ap.add_argument('--compat', default='NGAP_oai_compat.h')
    args = ap.parse_args()

    compat_path = os.path.join(args.dir, args.compat)
    if not os.path.exists(compat_path):
        print('compat header not found:', compat_path)
        sys.exit(1)

    # collect all names defined in generated headers (excluding compat itself)
    defined = set()
    for fn in sorted(os.listdir(args.dir)):
        if not fn.endswith('.h') or fn == args.compat:
            continue
        p = os.path.join(args.dir, fn)
        try:
            with open(p, encoding='utf-8', errors='replace') as f:
                in_enum = False
                for line in f:
                    m = DEFINE_RE.match(line)
                    if m:
                        defined.add(m.group(1))
                        continue
                    if line.startswith('typedef enum'):
                        in_enum = True
                        continue
                    if in_enum:
                        em = ENUM_MEMBER_RE.match(line)
                        if em:
                            defined.add(em.group(1))
                        if line.startswith('}'):
                            in_enum = False
        except OSError:
            pass

    with open(compat_path, encoding='utf-8', errors='replace') as f:
        lines = f.readlines()

    removed, kept = 0, 0
    out = []
    for line in lines:
        m = DEFINE_RE.match(line)
        if m and m.group(1) != 'NGAP_OAI_COMPAT_H' and m.group(1) in defined:
            removed += 1
            continue
        kept += 1
        out.append(line)

    with open(compat_path, 'w', encoding='utf-8') as f:
        f.writelines(out)

    print(f'compat defines: kept {kept}, removed (duplicated) {removed}')


if __name__ == '__main__':
    main()
