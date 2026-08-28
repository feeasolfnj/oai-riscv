#!/usr/bin/env python3
"""
fix_choice_values.py --prefix PREFIX --dir DIR [--aliases]

Restore "old-asn1c" value-member semantics in asn1c-844f9ca generated headers
(X2AP, NR RRC, S1AP, NGAP, ...).

asn1c-844f9ca is single-pass: members whose type is defined LATER in the ASN.1
module are emitted as POINTERS (both SEQUENCE members and CHOICE union
variants). OAI source was written against OAI's old asn1c which emitted:

  * CHOICE union variants      -> embedded VALUES
  * mandatory SEQUENCE members -> embedded VALUES   (asn_MBR opt field == 0)
  * optional SEQUENCE members  -> POINTERS          (asn_MBR opt field != 0)

This script converts a pointer member to a value member ONLY when the matching
asn_MBR entry in the .c file has flags == ATF_POINTER and opt == 0. The
844f9ca CHOICE/SEQUENCE runtime supports both layouts (it branches on
elm->flags & ATF_POINTER), so this is safe for encode/decode.

It also adds the missing "#include" of the member type's header (the by-value
containment graph of ASN.1 is acyclic, so no include cycles can occur).

Optional --aliases emits old-asn1c-style typedef aliases (ServedCells__Member
etc.) needed by the X2AP OAI source.

Idempotent.
"""

import argparse
import os
import re
import sys

INCLUDE_RE = re.compile(r'^#include\s+"([\w.-]+\.h)"')


def compute_scc(include_map):
    """Kosaraju strongly-connected components of the header include graph.

    Returns {file: component_id}. Two headers in the same SCC form an include
    cycle: converting a member of one to a VALUE would require the other
    header to be complete while it is still being expanded (include-guard
    trap), so such members must stay POINTERS.
    """
    files = list(include_map)
    index = {f: i for i, f in enumerate(files)}
    adj = [[index[n] for n in include_map[f] if n in index] for f in files]
    radj = [[] for _ in files]
    for u, vs in enumerate(adj):
        for v in vs:
            radj[v].append(u)

    sys.setrecursionlimit(100000)
    seen = [False] * len(files)
    order = []

    def dfs1(u):
        seen[u] = True
        for v in adj[u]:
            if not seen[v]:
                dfs1(v)
        order.append(u)

    for u in range(len(files)):
        if not seen[u]:
            dfs1(u)

    comp = [-1] * len(files)

    def dfs2(u, cid):
        comp[u] = cid
        for v in radj[u]:
            if comp[v] == -1:
                dfs2(v, cid)

    cid = 0
    for u in reversed(order):
        if comp[u] == -1:
            dfs2(u, cid)
            cid += 1
    return {f: comp[i] for i, f in enumerate(files)}


def normalize_includes(text):
    """Move '#include "X.h"' lines to the front include block:

    * from the tail 'Referred external types' block (asn1c-844f9ca puts
      forward-referenced type includes at the END of the header; after
      converting those members to VALUES the include must appear BEFORE the
      struct definition), and
    * from OUTSIDE the include guard (an earlier bug inserted them at the
      very top of the file).

    Insertion point: after the last '#include' line in the front block
    (guard-internal, before '#ifdef __cplusplus' / 'typedef struct'). Include
    guards break any (rare) cycles.

    Idempotent.
    """
    lines = text.splitlines(keepends=True)
    guard = tail = None
    for i, ln in enumerate(lines):
        if guard is None and re.match(r"^#ifndef\s+\S+_H_", ln):
            guard = i
        if tail is None and "Referred external types" in ln:
            tail = i

    moved = []
    keep = []
    for i, ln in enumerate(lines):
        if INCLUDE_RE.match(ln) and ((tail is not None and i >= tail)
                                     or (guard is not None and i < guard)):
            moved.append(ln)
        else:
            keep.append(ln)
    if not moved:
        return text

    # front block: up to the first typedef / forward declarations / extern "C"
    front = []
    for ln in keep:
        if (ln.startswith("typedef struct") or ln.startswith("/* Forward declarations")
                or ln.startswith("#ifdef __cplusplus")):
            break
        front.append(ln)
    last_inc = max([i for i, ln in enumerate(front) if ln.startswith("#include")],
                   default=-1)
    new_front = front[:last_inc + 1] + moved + front[last_inc + 1:]
    return "".join(new_front) + "".join(keep[len(front):])
ASN_DEF_RE = re.compile(
    r"\{ ([^,}]+), (\d+), offsetof\(struct (\w+), ((?:choice\.)?\w+)\),\s*"
    r"\(ASN_TAG_CLASS_\w+ \| \(\d+ << 2\)\),\s*"
    r"[+-]?\d+,[^\n]*\n[^\n]*&asn_DEF_(\w+),")
LOOSE_RE = re.compile(
    r"\{ ([^,}]+), (\d+), offsetof\(struct (\w+), ((?:choice\.)?\w+)\)")

# (header basename, member type struct tag, alias) -- only for X2AP
X2AP_ALIASES = [
    ("X2AP_ServedCells.h", "X2AP_ServedCells__ServedCells_Member",
     "ServedCells__Member"),
    ("X2AP_ServedNRcellsENDCX2ManagementList.h",
     "X2AP_ServedNRcellsENDCX2ManagementList__ServedNRcellsENDCX2ManagementList_Member",
     "ServedNRcellsENDCX2ManagementList__Member"),
    ("X2AP_ServedEUTRAcellsENDCX2ManagementList.h",
     "X2AP_ServedEUTRAcellsENDCX2ManagementList__ServedEUTRAcellsENDCX2ManagementList_Member",
     "ServedEUTRAcellsENDCX2ManagementList__Member"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prefix", default="X2AP_", help="type name prefix, e.g. NR_")
    ap.add_argument("--dir", required=True, help="directory of generated headers")
    ap.add_argument("--aliases", action="store_true",
                    help="add X2AP old-asn1c compound-member aliases")
    ap.add_argument("--no-choice", action="store_true",
                    help="keep CHOICE union variants as POINTERS (NR RRC needs this)")
    args = ap.parse_args()

    DIR = args.dir
    PREFIX = args.prefix
    ALIASES = X2AP_ALIASES if args.aliases else []

    struct_def_re = re.compile(r"^typedef struct (\w+) \{$")
    nested_struct_re = re.compile(r"^\s*struct (\w+) \{$")
    member_ptr_re = re.compile(
        r"^(\s*)(?:struct\s+)?(%s[A-Za-z0-9_]+?)(?:_t)?(\s+)\*(\s*)([A-Za-z_]\w*);\s*$"
        % re.escape(PREFIX))

    stats = {"converted": 0, "flags_flipped": 0, "flag_not_found": [],
             "reverted": 0, "alias_added": []}

    # tag -> header file that defines 'typedef struct tag {'
    tags = {}
    headers = sorted(fn for fn in os.listdir(DIR) if fn.endswith(".h"))
    for fn in headers:
        with open(os.path.join(DIR, fn), errors="surrogateescape") as f:
            for line in f:
                m = struct_def_re.match(line)
                if m:
                    tags.setdefault(m.group(1), fn)

    # header include graph + strongly-connected components (include cycles).
    # NOTE: match line-by-line, '^' does not anchor to line starts in a
    # multi-line finditer().
    include_map = {}
    for fn in headers:
        incs = set()
        with open(os.path.join(DIR, fn), errors="surrogateescape") as f:
            for ln in f:
                m = INCLUDE_RE.match(ln)
                if m and m.group(1) in headers:
                    incs.add(m.group(1))
        include_map[fn] = incs
    comp = compute_scc(include_map)

    def in_cycle(type_file, cur_file):
        return comp.get(type_file) is not None and \
            comp.get(type_file) == comp.get(cur_file)

    for fn in headers:
        if not fn.endswith(".h"):
            continue
        path = os.path.join(DIR, fn)
        with open(path, errors="surrogateescape") as f:
            text = f.read()

        c_path = path[:-2] + ".c"
        if os.path.exists(c_path):
            with open(c_path, errors="surrogateescape") as f:
                c_text = f.read()
            # index asn_MBR entries: (struct tag, member path) -> (flags, opt, asn_def)
            idx = {}
            for m in ASN_DEF_RE.finditer(c_text):
                idx[(m.group(3), m.group(4))] = (m.group(1).strip(), m.group(2), m.group(5))
            for m in LOOSE_RE.finditer(c_text):
                idx.setdefault((m.group(3), m.group(4)), (m.group(1).strip(), m.group(2), None))
        else:
            c_text = None
            idx = {}

        new_lines = []
        stack = []
        add_includes = set()
        converted = []

        for line in text.splitlines(keepends=True):
            m = struct_def_re.match(line)
            if m:
                stack.append(m.group(1))
                new_lines.append(line)
                continue
            m2 = nested_struct_re.match(line)
            if m2:
                stack.append(m2.group(1))
                new_lines.append(line)
                continue
            if not stack:
                new_lines.append(line)
                continue
            if re.match(r"^\s*\} choice;", line):
                new_lines.append(line)
                continue
            if re.match(r"^\s*\} \w+;", line):
                stack.pop()
                new_lines.append(line)
                continue
            # NOTE: members in an include cycle that were converted to VALUES
            # by an earlier run are NOT auto-reverted here (that would also
            # revert asn1c's original value members such as SetupRelease.setup
            # which OAI reads with '.choice.'). Use the dedicated
            # fix_setuprelease_cycle.py for the known SetupRelease cycle.
            pm = member_ptr_re.match(line)
            if pm:
                name = pm.group(5)
                cur_tag = stack[-1]
                choice_res = idx.get((cur_tag, "choice." + name))
                res = idx.get((cur_tag, name)) or choice_res
                if (res and res[0] == "ATF_POINTER" and res[1] == "0"
                        and not (args.no_choice and choice_res is not None)):
                    type_name = res[2] if res[2] else pm.group(2)
                    defining = tags.get(type_name)
                    # skip members in an include cycle: converting them to a
                    # VALUE would need the other header complete while it is
                    # still being expanded (include-guard trap)
                    if (defining is not None and defining != fn
                            and not in_cycle(defining, fn)):
                        new_lines.append("%s%s_t\t%s;\n" % (pm.group(1), type_name, name))
                        add_includes.add(defining)
                        converted.append((cur_tag, name))
                        stats["converted"] += 1
                        continue
            new_lines.append(line)

        new_text = "".join(new_lines)
        # insert missing includes in the FRONT include block (before any
        # member use); tail "Referred external types" includes are moved to
        # the front as well (see move_tail_includes_to_front).
        parts = new_text.split("#ifdef __cplusplus", 1)
        head = parts[0]
        missing = sorted(inc for inc in add_includes
                         if '#include "%s"' % inc not in head)
        if missing:
            front = head.splitlines(keepends=True)
            last_inc = max([i for i, ln in enumerate(front) if ln.startswith("#include")],
                           default=-1)
            insert = ["#include \"%s\"\n" % inc for inc in missing]
            new_text = "".join(front[:last_inc + 1]) + "".join(insert) + \
                       "".join(front[last_inc + 1:])
            if len(parts) == 2:
                new_text += "#ifdef __cplusplus" + parts[1]

        # normalize include placement (tail block / outside-guard -> front)
        new_text = normalize_includes(new_text)

        if new_text != text:
            with open(path, "w", errors="surrogateescape") as f:
                f.write(new_text)

        if converted and c_text is not None:
            changed = False
            for tag, member in converted:
                pat = re.compile(
                    r"\{ ATF_POINTER, 0, offsetof\(struct %s, ((?:choice\.)?%s)\)" % (
                        re.escape(tag), re.escape(member)))
                new_c, n = pat.subn(
                    lambda m: "{ ATF_NOFLAGS, 0, offsetof(struct %s, %s)" % (tag, m.group(1)),
                    c_text)
                if n:
                    c_text = new_c
                    changed = True
                    stats["flags_flipped"] += 1
                else:
                    stats["flag_not_found"].append((tag, member))
            if changed:
                with open(c_path, "w", errors="surrogateescape") as f:
                    f.write(c_text)

    if ALIASES:
        for header, member_tag, alias in ALIASES:
            h = os.path.join(DIR, header)
            if not os.path.exists(h):
                continue
            with open(h) as f:
                text = f.read()
            alias_line = "typedef %s %s;\n" % (member_tag, alias)
            if alias_line not in text:
                with open(h, "a", errors="surrogateescape") as f:
                    f.write("\n/* OAI old-asn1c compat alias (riscv-port) */\n" + alias_line)
                stats["alias_added"].append(alias)

    print("dir                : %s" % DIR)
    print("converted members  : %d" % stats["converted"])
    print("reverted to pointer: %d" % stats["reverted"])
    print("flags flipped in .c: %d" % stats["flags_flipped"])
    print("aliases added      : %s" % stats["alias_added"])
    for item in stats["flag_not_found"]:
        print("  WARN flag not found: %s.%s" % item)
    return 0


if __name__ == "__main__":
    sys.exit(main())
