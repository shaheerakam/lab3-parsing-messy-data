import csv
import re
import datetime
from collections import Counter

INPUT = "data/messy_samples.csv"
OUTPUT = "clean_samples.csv"

MONTHS = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
          "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12}

MMOL_TO_MGDL = 18.016


def clean_sample_id(raw):
    m = re.fullmatch(r"[sS]-?(\d{4})", raw.strip())
    if m:
        return "S" + m.group(1)
    return None


def clean_name(raw):
    # one letter, a period, spaces, then a last name. Fixes ALL-CAPS names.
    m = re.fullmatch(r"([A-Za-z])\.\s+([A-Za-z]+)", raw.strip())
    if m:
        return m.group(1).upper() + ". " + m.group(2).capitalize()
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
    m = re.fullmatch(r"\s*site[\s_-]*([abc])\s*", raw, re.IGNORECASE)
    if m:
        return "Site " + m.group(1).upper()
    return None


def clean_unit(raw):
    s = raw.strip()
    if re.fullmatch(r"mg/dl", s, re.IGNORECASE):
        return "mg/dL"
    if re.fullmatch(r"mmol/l", s, re.IGNORECASE):
        return "mmol/L"
    return None


def clean_glucose(raw, unit):
    """Returns (value_in_mg_dl, flag_text). Blank value means missing."""
    v = raw.strip()
    if v == "" or v.upper() == "N/A":
        return "", "missing_value"
    m = re.fullmatch(r"(\d+(?:\.\d+)?)(\*?)", v)
    if not m:
        return "", "unparseable_value"
    number = float(m.group(1))
    flags = []
    if m.group(2) == "*":
        flags.append("asterisk_removed")
    if unit == "mmol/L":
        number = number * MMOL_TO_MGDL
        flags.append("converted_from_mmol")
    elif unit is None:
        return "", "unrecognized_unit"
    if not (20 <= number <= 600):
        flags.append("implausible_after_conversion")
    return round(number, 1), ";".join(flags)


def clean_dob(raw):
    s = raw.strip()
    year = month = day = None

    # Format 1: 1997-12-02  (year-month-day)
    m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", s)
    if m:
        year, month, day = int(m.group(1)), int(m.group(2)), int(m.group(3))
    else:
        # Format 2: 07/09/1962  (month/day/year)
        m = re.fullmatch(r"(\d{2})/(\d{2})/(\d{4})", s)
        if m:
            month, day, year = int(m.group(1)), int(m.group(2)), int(m.group(3))
        else:
            # Format 3: 21-Jun-1997  (day-monthname-year)
            m = re.fullmatch(r"(\d{2})-([A-Za-z]{3})-(\d{4})", s)
            if m:
                day = int(m.group(1))
                month = MONTHS.get(m.group(2).lower())
                year = int(m.group(3))
            else:
                # Format 4: 11.24.53  (month.day.two-digit-year)
                m = re.fullmatch(r"(\d{2})\.(\d{2})\.(\d{2})", s)
                if m:
                    month, day, yy = int(m.group(1)), int(m.group(2)), int(m.group(3))
                    year = 1900 + yy if yy >= 50 else 2000 + yy
                else:
                    return None  # no format matched

    try:
        return datetime.date(year, month, day).isoformat()
    except (ValueError, TypeError):
        return None  # impossible date, e.g. month 13


with open(INPUT, newline="") as f:
    rows = list(csv.DictReader(f))

COLUMNS = ["sample_id", "patient_name", "dob", "sex", "enrollment_site",
           "glucose_mg_dl", "glucose_original_value", "glucose_original_unit",
           "glucose_flag", "notes"]

clean_rows = []
flag_counts = Counter()
for row in rows:
    unit = clean_unit(row["glucose_unit"])
    glucose, flag = clean_glucose(row["glucose_value"], unit)
    new_row = {
        "sample_id": clean_sample_id(row["sample_id"]),
        "patient_name": clean_name(row["patient_name"]),
        "dob": clean_dob(row["dob"]),
        "sex": clean_sex(row["sex"]),
        "enrollment_site": clean_site(row["enrollment_site"]),
        "glucose_mg_dl": glucose,
        "glucose_original_value": row["glucose_value"].strip(),
        "glucose_original_unit": unit,
        "glucose_flag": flag,
        "notes": row["notes"].strip(),
    }
    for col in ["sample_id", "patient_name", "dob", "sex",
                "enrollment_site", "glucose_original_unit"]:
        if new_row[col] is None:
            print("PROBLEM with", col, ":", repr(row[col]))
    if flag in ("unparseable_value", "unrecognized_unit"):
        print("PROBLEM with glucose:", repr(row["glucose_value"]), repr(row["glucose_unit"]))
    for one_flag in flag.split(";"):
        if one_flag:
            flag_counts[one_flag] += 1
    clean_rows.append(new_row)

with open(OUTPUT, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=COLUMNS)
    writer.writeheader()
    writer.writerows(clean_rows)

print("Done. Wrote", len(clean_rows), "rows to", OUTPUT)
print("Flag counts:", dict(flag_counts))