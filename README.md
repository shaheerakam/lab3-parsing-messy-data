# Lab 3: Parsing Messy Health Data (PUBH 4201)

This repo cleans `messy_samples.csv` (60 synthetic clinical sample records) two ways, with hand-written regular expressions and with a generative AI tool, then compares the results.

Undergraduate track: I cleaned one file (`messy_samples.csv`). I did not do the FASTA file.

## What's in this repo

| File | What it is |
|---|---|
| `data/messy_samples.csv` | The raw messy input (generated, see "Getting the data") |
| `data/messy_sequences.fasta` | Course FASTA file (copied in, not used for this lab) |
| `clean_samples.py` | Regex cleaning script (Task 1) |
| `clean_samples.csv` | Output of the regex script |
| `ai_clean_samples.csv` | Output of the AI-assisted cleaning (Task 2) |
| `compare.py` | Script that lists every cell where the two tables differ (Task 3) |
| `comparison_diffs.csv` | Output of `compare.py` |
| `AI_USAGE.md` | AI tools used, the exact prompt, and notes on the AI's output |
| `WRITEUP.md` | Comparison write-up: agreement, disagreement, failure modes, trust |
| `NOTES.md` | My first observations of the messy data |

## Requirements

- Python 3 (tested with `python3` on macOS)
- No installs needed. The scripts use only Python's built-in `csv`, `re`, `datetime`, and `collections` modules.

## Getting the data

`messy_samples.csv` was not in the course repo (only `generate_data.py`, the FASTA file, and `SOURCE.md` were). I created it by running the instructor's seeded generator (seed 42) from inside my own `data` folder:

```
cd data
python3 /path/to/applied-computing-HDS/data/raw/lab3-messy-data/generate_data.py
cd ..
```

This writes `messy_samples.csv` and `messy_sequences.fasta` into `data/`. I confirmed the regenerated FASTA was identical to the instructor's copy (`diff` printed nothing). The CSV is already included in this repo, so you do not need to regenerate it.

## How to run the regex script

Run from the repo root (the folder that contains `clean_samples.py`):

```
python3 clean_samples.py
```

- **Input:** `data/messy_samples.csv` (columns: sample_id, patient_name, dob, sex, enrollment_site, glucose_value, glucose_unit, notes)
- **Output:** `clean_samples.csv` in the repo root
- **Console output:** any value the patterns did not recognize is printed as a `PROBLEM` line. On this data there are none. It also prints "Done. Wrote 60 rows" and a count of each flag.

Expected console output:

```
Done. Wrote 60 rows to clean_samples.csv
Flag counts: {'converted_from_mmol': 12, 'implausible_after_conversion': 12, 'missing_value': 2, 'asterisk_removed': 2}
```

### Output columns

| Column | Meaning |
|---|---|
| `sample_id` | Standardized to `S0001` style |
| `patient_name` | Standardized to `A. Smith` style |
| `dob` | `YYYY-MM-DD` |
| `sex` | `M`, `F`, or `Unknown` |
| `enrollment_site` | `Site A`, `Site B`, or `Site C` |
| `glucose_mg_dl` | Glucose in mg/dL (mmol/L values multiplied by 18.016); blank if missing |
| `glucose_original_value` | Original glucose text, unchanged |
| `glucose_original_unit` | Original unit, standardized to `mg/dL` or `mmol/L` |
| `glucose_flag` | Semicolon-separated flags: `missing_value`, `asterisk_removed`, `converted_from_mmol`, `implausible_after_conversion` |
| `notes` | Carried over unchanged |

### Assumptions the script makes

- Slash dates (`07/09/1962`) and dotted dates (`11.24.53`) are month first. The file proves this for many rows (for example `12/16/1974`), but a few dotted dates are truly ambiguous (see `WRITEUP.md`).
- Two-digit years 50-99 become 1950-1999, and 00-49 become 2000-2049.
- A blank `sex` is treated as `Unknown`.
- `N/A` glucose becomes blank and is flagged, not dropped. A trailing `*` is removed and flagged.
- Glucose values outside 20-600 mg/dL after conversion are flagged as implausible. The script still converts