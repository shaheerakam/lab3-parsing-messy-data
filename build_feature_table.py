import csv
import datetime

INPUT = "clean_samples.csv"
OUTPUT = "feature_table.csv"
REFERENCE_DATE = datetime.date(2026, 9, 21)  # fixed so results are reproducible

COLUMNS = ["sample_id",
           "glucose_mg_dl", "glucose_usable_mg_dl", "age_years",
           "glucose_missing", "glucose_implausible",
           "sex", "enrollment_site", "dob", "glucose_flag", "notes"]


def age_on(dob_text, ref):
    d = datetime.date.fromisoformat(dob_text)
    had_birthday = (ref.month, ref.day) >= (d.month, d.day)
    return ref.year - d.year - (0 if had_birthday else 1)


with open(INPUT, newline="") as f:
    rows = list(csv.DictReader(f))

table = []
for r in rows:
    glucose = r["glucose_mg_dl"]
    flag = r["glucose_flag"]
    missing = 1 if glucose == "" else 0
    implausible = 1 if "implausible_after_conversion" in flag else 0
    usable = "" if (missing or implausible) else glucose
    table.append({
        "sample_id": r["sample_id"],
        "glucose_mg_dl": glucose,
        "glucose_usable_mg_dl": usable,
        "age_years": age_on(r["dob"], REFERENCE_DATE),
        "glucose_missing": missing,
        "glucose_implausible": implausible,
        "sex": r["sex"],
        "enrollment_site": r["enrollment_site"],
        "dob": r["dob"],
        "glucose_flag": flag,
        "notes": r["notes"],
    })

with open(OUTPUT, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=COLUMNS)
    w.writeheader()
    w.writerows(table)

# ---- readiness summary ----
n = len(table)
ids = {t["sample_id"] for t in table}
print("Rows:", n, "| unique sample_ids:", len(ids))
print("Glucose missing:", sum(t["glucose_missing"] for t in table))
print("Glucose implausible (excluded from usable):",
      sum(t["glucose_implausible"] for t in table))
print("Usable glucose values:",
      sum(1 for t in table if t["glucose_usable_mg_dl"] != ""))
print("Sex counts:", {s: sum(1 for t in table if t["sex"] == s)
                      for s in sorted({t["sex"] for t in table})})
print("Site counts:", {s: sum(1 for t in table if t["enrollment_site"] == s)
                       for s in sorted({t["enrollment_site"] for t in table})})
ages = [t["age_years"] for t in table]
print("Age range:", min(ages), "to", max(ages))
print("Wrote", OUTPUT)