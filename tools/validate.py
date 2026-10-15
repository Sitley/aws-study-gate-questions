#!/usr/bin/env python3
"""Validate every question pack in this repository.

Usage: python3 tools/validate.py [bank]   (default bank: clf)
Exits non-zero and prints the problems if anything is wrong.
"""
import json, re, sys, pathlib

DOMAINS = {
    "Cloud Concepts",
    "Security and Compliance",
    "Cloud Technology and Services",
    "Billing, Pricing, and Support",
}

def main():
    bank = sys.argv[1] if len(sys.argv) > 1 else "clf"
    root = pathlib.Path(__file__).resolve().parent.parent / bank
    index = json.loads((root / "index.json").read_text(encoding="utf-8"))
    problems, ids, total = [], {}, 0
    for name in index["packs"]:
        if not re.fullmatch(r"pack-\d{3}\.json", name):
            problems.append(f"{name}: file name must be pack-NNN.json")
            continue
        path = root / name
        if not path.exists():
            problems.append(f"{name}: listed in index.json but missing")
            continue
        pack = json.loads(path.read_text(encoding="utf-8"))
        for q in pack.get("questions", []):
            qid = q.get("id", "?")
            if q.get("retired"):
                continue
            total += 1
            where = f"{name}:{qid}"
            if qid in ids and ids[qid] != name:
                problems.append(f"{where}: id already used in {ids[qid]}")
            ids[qid] = name
            if q.get("domain") not in DOMAINS:
                problems.append(f"{where}: unknown domain {q.get('domain')!r}")
            opts = q.get("options", [])
            ans = q.get("answer", [])
            if not isinstance(ans, list) or not ans or len(set(ans)) != len(ans):
                problems.append(f"{where}: answer must be a non-empty list without repeats")
                continue
            if not all(isinstance(a, int) and 0 <= a < len(opts) for a in ans):
                problems.append(f"{where}: answer index out of range")
            m = re.search(r"(\d)つ選べ", q.get("q", ""))
            if len(ans) > 1:
                if len(opts) < 5:
                    problems.append(f"{where}: multi-answer questions need 5+ options")
                if not m or int(m.group(1)) != len(ans):
                    problems.append(f"{where}: question text must end with 「{len(ans)}つ選べ。」")
            else:
                if len(opts) != 4:
                    problems.append(f"{where}: single-answer questions need exactly 4 options")
                if m:
                    problems.append(f"{where}: single-answer question says 「つ選べ」")
            for i, o in enumerate(opts):
                for k in ("text", "summary", "why", "use"):
                    if not isinstance(o, dict) or not o.get(k):
                        problems.append(f"{where}: option {i + 1} missing {k}")
            if not q.get("point"):
                problems.append(f"{where}: missing point")
            # Packs from pack-008 on must carry the date they were added and verified.
            if int(name[5:8]) >= 8:
                for k in ("added", "verified"):
                    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(q.get(k, ""))):
                        problems.append(f"{where}: {k} must be YYYY-MM-DD")
            docs = q.get("docs") or []
            if not docs or not all(re.match(r"https://(docs\.aws\.amazon\.com|aws\.amazon\.com|calculator\.aws|repost\.aws)/", u) for u in docs):
                problems.append(f"{where}: docs must be official AWS URLs")
    if problems:
        print("\n".join(problems))
        print(f"\n{len(problems)} problem(s)")
        sys.exit(1)
    print(f"OK: {len(index['packs'])} packs, {total} questions, highest id {max(ids, key=lambda s: int(s.split('-')[1]))}")

if __name__ == "__main__":
    main()
