import csv

REGEX_FILE = "clean_sequences.csv"
AI_FILE = "ai_clean_sequences.csv"
OUT_FILE = "comparison_sequences_diffs.csv"

FIELDS = ["organism", "gene", "header_length_bp", "actual_length_bp", "note"]


def load(path):
    rows = {}
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            clean = {k.strip(): (v or "").strip() for k, v in r.items() if k}
            rows[clean["sample_id"]] = clean
    return rows


regex_rows = load(REGEX_FILE)
ai_rows = load(AI_FILE)

diffs = []
for sid in sorted(set(regex_rows) | set(ai_rows)):
    if sid not in regex_rows:
        diffs.append((sid, "(row)", "MISSING", "present"))
        continue
    if sid not in ai_rows:
        diffs.append((sid, "(row)", "present", "MISSING"))
        continue
    for field in FIELDS:
        a = regex_rows[sid].get(field, "")
        b = ai_rows[sid].get(field, "")
        if a != b:
            diffs.append((sid, field, a, b))

with open(OUT_FILE, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["sample_id", "column", "regex_value", "ai_value"])
    w.writerows(diffs)

print("Rows in regex file:", len(regex_rows))
print("Rows in AI file:   ", len(ai_rows))
print("Total disagreements:", len(diffs))
print("Wrote details to", OUT_FILE)