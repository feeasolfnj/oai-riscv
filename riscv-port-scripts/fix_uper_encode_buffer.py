#!/usr/bin/env python3
"""fix_uper_encode_buffer.py

asn1c-844f9ca uper_encode_to_buffer() takes a 5th 'constraints' argument:
    uper_encode_to_buffer(td, constraints, sptr, buffer, buffer_size)
while OAI source (written against the old asn1c) calls it with 4 args:
    uper_encode_to_buffer(&asn_DEF_X, sptr, buffer, size)

This script inserts a NULL constraints argument into all OAI source call
sites (openair2/ openair3/ minus the generated */MESSAGES/* dirs).

Idempotent. Usage: python3 fix_uper_encode_buffer.py
"""

import os
import re
import sys

ROOT = "/home/kongbai/openairinterface5g"

PAT = re.compile(r"uper_encode_to_buffer\(\s*&asn_DEF_(\w+),")

def main():
    n = 0
    for sub in ("openair2", "openair3"):
        for dirpath, dirnames, filenames in os.walk(os.path.join(ROOT, sub)):
            # skip generated asn1c output, but still handle handwritten
            # asn1_msg.c which lives inside the MESSAGES dirs
            for fn in filenames:
                if not fn.endswith((".c", ".h")):
                    continue
                if "/MESSAGES/" in dirpath and fn != "asn1_msg.c":
                    continue
                path = os.path.join(dirpath, fn)
                with open(path, errors="surrogateescape") as f:
                    text = f.read()
                new_text, k = PAT.subn(
                    lambda m: "uper_encode_to_buffer(&asn_DEF_%s, NULL," % m.group(1),
                    text)
                if k:
                    with open(path, "w") as f:
                        f.write(new_text)
                    n += k
    print("call sites updated: %d" % n)
    return 0

if __name__ == "__main__":
    sys.exit(main())
