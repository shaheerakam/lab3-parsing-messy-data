import csv

REGEX_FILE = "clean_samples.csv"
AI_FILE = "ai_clean_samples.csv"
OUT_FILE = "comparison_diffs.csv"

FIELDS = [
    # (name, column in regex file, column in AI file)
    ("patient_name", "patient_name", "patient_name"),
    ("dob", "dob", "dob"),
    ("sex", "sex", "sex"),
    ("enrollment_site", "enrollment_site", "enrollment_site"),
    ("glucose_mg_dl", "glucose_mg_dl", "glucose_mg_dl"),
    ("notes", "notes", "notes"),
]


def load(path):
    with open(path, newline="") as f:
        rows = {}
        for r in csv.DictReader(f):
            clean = {k.strip(): (v or "").strip() for k, v in r.items() if k}
            rows[clean["sample_id"]] = clean
        return rows


def same(field, a, b):
    if field == "glucose_mg_dl":
        if a == "" and b == "":
            return True
        if a == "" or b == "":
            return False
        return abs(float(a) - float(b)) < 0.05
    return a == b


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
    for name, rcol, acol in FIELDS:
        a = regex_rows[sid].get(rcol, "")
        b = ai_rows[sid].get(acol, "")
        if not same(name, a, b):
            diffs.append((sid, name, a, b))

with open(OUT_FILE, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["sample_id", "column", "regex_value", "ai_value"])
    w.writerows(diffs)

print("Rows in regex file:", len(regex_rows))
print("Rows in AI file:   ", len(ai_rows))
print