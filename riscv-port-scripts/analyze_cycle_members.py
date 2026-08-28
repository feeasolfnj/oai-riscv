#!/usr/bin/env python3
"""
analyze_cycle_members.py --dir DIR

Find all VALUE members (non-pointer) whose type lives in another header that is
in the same SCC (include cycle) as the member's own header.

asn1c (940dd5fa) only pointer-izes DIRECT self-references.  Indirect cycles
(A -> B -> ... -> A via SetupRelease fan-in) emit by-value members which then
fall into the include-guard trap: the type's header is already being expanded
(guard open) but the definition comes later, so the type is invisible.

Output (TSV):  header, line, member_type, member_name
"""

import argparse
import os
import re
import sys

INCLUDE_RE = re.compile(r'^#include\s+"([\w.-]+\.h)"')
# struct member: "Type\t member;"   (no '*')
MEMBER_RE = re.compile(
    r'^\s+([A-Za-z_][\w]*(?:_\w+)*_t)\s+([a-zA-Z_]\w*)\s*;\s*$'
)


def compute_scc(include_map):
    files = list(include_map)
    index = {f: i for i, f in enumerate(files)}
    adj = [[index[n] for n in include_map[f] if n in index] for f in files]
    radj = [[] for _ in files]
    for u, vs in enumerate(adj):
        for v in vs:
            radj[v].append(u)

    sys.setrecursionlimit(200000)
    seen = [False] * len(files)
    order = []

    def dfs1(u):
        seen[u] = True
        for v in adj[u]:
            if not seen[v]:
                dfs1(v)
        order.append(u)

    for i in range(len(files)):
        if not seen[i]:
            dfs1(i)

    comp = [-1] * len(files)
    ncomp = 0

    def dfs2(u):
        comp[u] = ncomp
        for v in radj[u]:
            if comp[v] == -1:
                dfs2(v)

    for u in reversed(order):
        if comp[u] == -1:
            dfs2(u)
            ncomp += 1
    return {f: comp[index[f]] for f in files}, ncomp


def type_to_header(prefix, type_name):
    """NR_DMRS_UplinkConfig_t -> NR_DMRS-UplinkConfig.h"""
    if not type_name.startswith(prefix):
        return None
    body = type_name[len(prefix):]
    if body.endswith('_t'):
        body = body[:-2]
    return prefix + body.replace('_', '-') + '.h'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dir', required=True)
    ap.add_argument('--prefix', default='NR_')
    args = ap.parse_args()

    headers = {}
    for fn in os.listdir(args.dir):
        if fn.endswith('.h') and fn.startswith(args.prefix):
            headers[fn] = os.path.join(args.dir, fn)

    include_map = {}
    for fn, path in headers.items():
        incs = set()
        try:
            with open(path, encoding='utf-8', errors='replace') as f:
                for line in f:
                    m = INCLUDE_RE.match(line.strip())
                    if m and m.group(1) in headers:
                        incs.add(m.group(1))
        except OSError:
            pass
        include_map[fn] = incs

    comp, ncomp = compute_scc(include_map)

    # headers in non-trivial SCCs (cycle size > 1)
    comp_size = {}
    for c in comp.values():
        comp_size[c] = comp_size.get(c, 0) + 1
    cyclic = {c for c, n in comp_size.items() if n > 1}

    print(f'# headers: {len(headers)}, SCCs: {ncomp}, cyclic headers: '
          f'{sum(1 for c in comp.values() if c in cyclic)}')

    hits = []
    for fn, path in sorted(headers.items()):
        if comp[fn] not in cyclic:
            continue
        try:
            with open(path, encoding='utf-8', errors='replace') as f:
                for lineno, line in enumerate(f, 1):
                    m = MEMBER_RE.match(line)
                    if not m:
                        continue
                    mtype, mname = m.group(1), m.group(2)
                    th = type_to_header(args.prefix, mtype)
                    if th and th in headers and comp[th] == comp[fn]:
                        hits.append((fn, lineno, mtype, mname, th))
        except OSError:
            pass

    print(f'# value members whose type is in the same cycle: {len(hits)}')
    for h in hits:
        print('\t'.join(str(x) for x in h))


if __name__ == '__main__':
    main()
