import csv
import re

INPUT = "data/messy_sequences.fasta"
OUTPUT = "clean_sequences.csv"


def read_fasta(path):
    """Returns a list of (header_text, full_sequence) pairs."""
    records = []
    header = None
    seq_parts = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line.startswith(">"):
                if header is not None:
                    records.append((header, "".join(seq_parts)))
                header = line[1:]
                seq_parts = []
            elif line:
                seq_parts.append(line)
    if header is not None:
        records.append((header, "".join(seq_parts)))
    return records


def clean_id(header):
    # sample or seq, optional _ or -, then digits. Padded to 3 digits.
    m = re.match(r"(?:sample|seq)[_-]?(\d+)", header, re.IGNORECASE)
    if m:
        return "sample_" + format(int(m.group(1)), "03d")
    return None


def clean_organism(header):
    # matches Homo_sapiens, Homo sapiens, H.sapiens, Hsapiens
    if re.search(r"H(?:omo)?[._ ]?sapiens", header, re.IGNORECASE):
        return "Homo sapiens"
    return None


def clean_gene(header):
    # Case 1: a label like gene=BRCA1, gene:TP53, or target=BRCA1.
    # [\w-]+ includes the hyphen so symbols like HLA-DRB1 don't get cut off.
    m = re.search(r"(?:gene|target)[=:]\s*([\w-]+)", header, re.IGNORECASE)
    if m:
        return m.group(1).upper()
    # Case 2: no label, so look for an ALL-CAPS symbol sitting between | or ; separators
    m = re.search(r"[|;]\s*([A-Z][A-Z0-9-]{2,})\s*(?=[|;]|$)", header)
    if m:
        return m.group(1)
    return None


def clean_header_length(header):
    m = re.search(r"len(?:gth)?[=:]\s*(\d+)", header, re.IGNORECASE)
    if m:
        return int(m.group(1))
    m = re.search(r"(\d+)\s*bp", header, re.IGNORECASE)
    if m:
        return int(m.group(1))
    return None  # no usable number in the header


def clean_note(header):
    m = re.search(r"note[=:]\s*([^|;]+)", header, re.IGNORECASE)
    return m.group(1).strip() if m else ""


records = read_fasta(INPUT)

COLUMNS = ["sample_id", "organism", "gene", "header_length_bp",
           "actual_length_bp", "length_check", "note", "raw_header"]

clean_rows = []
check_counts = {}
for header, seq in records:
    hlen = clean_header_length(header)
    actual = len(seq)
    if hlen is None:
        if re.search(r"len(?:gth)?[=:]\s*NA", header, re.IGNORECASE):
            check = "header_length_is_NA"
        else:
            check = "no_length_in_header"
    elif hlen == actual:
        check = "match"
    else:
        check = "MISMATCH"
    check_counts[check] = check_counts.get(check, 0) + 1

    new_row = {
        "sample_id": clean_id(header),
        "organism": clean_organism(header),
        "gene": clean_gene(header),
        "header_length_bp": "" if hlen is None else hlen,
        "actual_length_bp": actual,
        "length_check": check,
        "note": clean_note(header),
        "raw_header": header,
    }
    for col in ["sample_id", "organism", "gene"]:
        if new_row[col] is None:
            print("PROBLEM with", col, ":", repr(header))
    clean_rows.append(new_row)

with open(OUTPUT, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=COLUMNS)
    writer.writeheader()
    writer.writerows(clean_rows)

print("Done. Wrote", len(clean_rows), "rows to", OUTPUT)
print("Length checks:", check_counts)