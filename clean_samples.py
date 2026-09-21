import csv
import re

INPUT = "data/messy_samples.csv"
OUTPUT = "clean_samples.csv"


def clean_sample_id(raw):
    # [sS] = s or S, -? = optional hyphen, (\d{4}) = exactly 4 digits
    m = re.fullmatch(r"[sS]-?(\d{4})", raw.strip())
    if m:
        return "S" + m.group(1)
    return None


def clean_sex(raw):
    s = raw.strip()
    if s == "":
        return "Unknown"  # blank treated same as unknown (documented decision)
    if re.fullmatch(r"m(ale)?", s, re.IGNORECASE):
        return "M"
    if re.fullmatch(r"f(emale)?", s, re.IGNORECASE):
        return "F"
    if re.fullmatch(r"u(nknown)?", s, re.IGNORECASE):
        return "Unknown"
    return None


def clean_site(raw):
    # "site", then optional space/underscore/hyphen, then a letter A-C, then optional trailing space
    m = re.fullmatch(r"\s*site[\s_-]*([abc])\s*", raw, re.IGNORECASE)
    if m:
        return "Site " + m.group(1).upper()
    return None


with open(INPUT, newline="") as f:
    rows = list(csv.DictReader(f))

clean_rows = []
for row in rows:
    new_row = {
        "sample_id": clean_sample_id(row["sample_id"]),
        "sex": clean_sex(row["sex"]),
        "enrollment_site": clean_site(row["enrollment_site"]),
    }
    for col in ["sample_id", "sex", "enrollment_site"]:
        if new_row[col] is None:
            print("PROBLEM with", col, ":", repr(row[col]))
    clean_rows.append(new_row)

with open(OUTPUT, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["sample_id", "sex", "enrollment_site"])
    writer.writeheader()
    writer.writerows(clean_rows)

print("Done. Wrote", len(clean_rows), "rows to", OUTPUT)
