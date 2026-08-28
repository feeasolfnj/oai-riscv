#!/usr/bin/env python3
"""
fix_cycle_members.py --prefix PREFIX --dir DIR [--fix]

Pointer-ize VALUE members whose type lives in a header that is in the same
SCC (include cycle) as the member's own header.  This is the asn1c-940dd5fa
indirect-cycle trap (A -> B -> ... -> A via SetupRelease fan-in).

Fix:
    .h:  typedef struct <Tag> <Type_t>;   (forward decl, if missing)
         Type_t\t*member;                 (if currently by value)
    .c:  asn_MBR flags ATF_NOFLAGS -> ATF_POINTER   (for that member)

Idempotent.  Run without --fix for a dry-run report.
"""

import argparse
import os
import re
import sys

INCLUDE_RE = re.compile(r'^#include\s+"([\w.-]+\.h)"')
MEMBER_RE = re.compile(
    r'^(\s+)([A-Za-z_][\w]*(?:_\w+)*_t)(\s+)(\*?)([a-zA-Z_]\w*)(\s*;\s*)$'
)
FWD_RE = re.compile(r'^typedef struct (\w+) (\w+_t);\s*$')


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
    ap.add_argument('--fix', action='store_true',
                    help='apply fixes (default: dry-run report)')
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

    comp, _ = compute_scc(include_map)
    comp_size = {}
    for c in comp.values():
        comp_size[c] = comp_size.get(c, 0) + 1
    cyclic = {c for c, n in comp_size.items() if n > 1}

    nfix = 0
    for fn in sorted(headers):
        if comp[fn] not in cyclic:
            continue
        path = headers[fn]
        try:
            with open(path, encoding='utf-8', errors='replace') as f:
                lines = f.readlines()
        except OSError:
            continue

        targets = []  # (lineno, member_name, type_name)
        for lineno, line in enumerate(lines, 1):
            m = MEMBER_RE.match(line)
            if not m:
                continue
            indent, mtype, ws, star, mname, tail = m.groups()
            if star:  # already pointer
                continue
            th = type_to_header(args.prefix, mtype)
            if th and th in headers and comp[th] == comp[fn]:
                targets.append((lineno, mname, mtype))

        if not targets:
            continue

        # forward decls (dedupe against existing)
        fwd_to_add = []
        for _, mname, mtype in targets:
            tag = mtype[len(args.prefix):-2]
            fwd = f'typedef struct {args.prefix}{tag} {mtype};\n'
            exists = any(FWD_RE.match(l.strip()) and
                         FWD_RE.match(l.strip()).group(2) == mtype
                         for l in lines)
            if not exists:
                fwd_to_add.append(fwd)

        if not args.fix:
            print(f'[dry-run] {fn}: pointer-ize '
                  f'{", ".join(t[1] for t in targets)}')
            continue

        # rewrite header
        out = []
        inserted = False
        for line in lines:
            m = MEMBER_RE.match(line)
            if m:
                indent, mtype, ws, star, mname, tail = m.groups()
                if (mtype, mname) in [(t[2], t[1]) for t in targets]:
                    star = '*'
                line = f'{indent}{mtype}{ws}{star}{mname}{tail}'
            if not inserted and line.startswith(f'typedef struct NR_'):
                for fwd in fwd_to_add:
                    out.append(fwd)
                inserted = True
            out.append(line)
        with open(path, 'w', encoding='utf-8') as f:
            f.writelines(out)
        nfix += 1
        print(f'[fix] {fn}: pointer-ized {[t[1] for t in targets]}')

        # .c asn_MBR flags
        cpath = os.path.join(args.dir, fn[:-2] + '.c')
        if os.path.exists(cpath):
            with open(cpath, encoding='utf-8', errors='replace') as f:
                clines = f.readlines()
            changed = False
            for i, cl in enumerate(clines):
                mm = re.match(r'\s*\{\s*ATF_NOFLAGS,\s*0,'
                              r' offsetof\(struct \w+, '
                              r'(\w+)\)', cl)
                if mm and mm.group(1) in [t[1] for t in targets]:
                    clines[i] = cl.replace('ATF_NOFLAGS', 'ATF_POINTER', 1)
                    changed = True
            if changed:
                with open(cpath, 'w', encoding='utf-8') as f:
                    f.writelines(clines)
                print(f'[fix] {os.path.basename(cpath)}: '
                      f'flags -> ATF_POINTER')

    print(f'# headers fixed: {nfix}')


if __name__ == '__main__':
    main()
