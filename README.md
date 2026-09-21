# Lab 3: Parsing Messy Health Data (PUBH 4201)

This repo cleans `messy_samples.csv` (60 synthetic clinical sample records) two ways, with hand-written regular expressions and with a generative AI tool, then compares the results.

Undergraduate track: I cleaned `messy_samples.csv` for the main lab. I also completed the optional extra credit: `messy_sequences.fasta` (regex and AI, compared) and a samples x features x metadata table.

## What's in this repo

| File | What it is |
|---|---|
| `data/messy_samples.csv` | The raw messy input (generated, see "Getting the data") |
| `data/messy_sequences.fasta` | Course FASTA file (used for the extra credit) |
| `clean_samples.py` | Regex cleaning script (Task 1) |
| `clean_samples.csv` | Output of the regex script |
| `ai_clean_samples.csv` | Output of the AI-assisted cleaning (Task 2) |
| `compare.py` | Script that lists every cell where the two tables differ (Task 3) |
| `comparison_diffs.csv` | Output of `compare.py` |
| `clean_sequences.py` | Extra credit: regex parsing of the FASTA headers |
| `clean_sequences.csv` | Output of `clean_sequences.py` |
| `ai_clean_sequences.csv` | Extra credit: AI-parsed version of the FASTA headers |
| `compare_sequences.py` | Extra credit: lists FASTA disagreements |
| `comparison_sequences_diffs.csv` | Output of `compare_sequences.py` |
| `build_feature_table.py` | Extra credit: builds the samples x features x metadata table |
| `feature_table.csv` | Output of `build_feature_table.py` |
| `AI_USAGE.md` | AI tools used, the exact prompts, and notes on the AI's output |
| `WRITEUP.md` | Comparison write-up: agreement, disagreement, failure modes, trust, extra credit |
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
- Glucose values outside 20-600 mg/dL after conversion are flagged as implausible. The script still converts them.

## How to run the comparison

After `clean_samples.py` and with `ai_clean_samples.csv` present:

```
python3 compare.py
```

This writes `comparison_diffs.csv`, with one line per cell where the regex table and the AI table disagree (columns: sample_id, column, regex_value, ai_value). Expected result: 60 rows in each table and 4 disagreements, all in `sex`.

## AI-assisted cleaning (Task 2)

I uploaded `messy_samples.csv` to a fresh AI chat with a single prompt. The full prompt, the AI's chat response, and my notes are in `AI_USAGE.md`. I pasted the CSV text it produced into `ai_clean_samples.csv`. To reproduce this, paste the prompt from `AI_USAGE.md` into an AI tool with the raw file attached. Results can vary between runs, so the output may not be identical.

## Extra credit: FASTA and feature table

Run in this order from the repo root:

```
python3 clean_sequences.py
python3 compare_sequences.py
python3 build_feature_table.py
```

- `clean_sequences.py` reads `data/messy_sequences.fasta` and writes `clean_sequences.csv` (8 rows, no `PROBLEM` lines). It also measures the real sequence length and compares it with the length stated in the header.
- `compare_sequences.py` compares `clean_sequences.csv` with `ai_clean_sequences.csv` and writes `comparison_sequences_diffs.csv`. Expected result: 8 rows in each table and 0 disagreements.
- `build_feature_table.py` reshapes `clean_samples.csv` into `feature_table.csv`, one row per sample (60 rows) with feature and metadata columns. Age is computed at a fixed reference date (2026-09-21) so results are reproducible. Expected: 60 unique sample_ids, 2 missing glucose, 12 implausible, 46 usable.

Findings: both approaches agreed on all 8 FASTA records. Only 1 of the 3 headers with a stated length matches the real sequence length (sample_003: stated 150, actual 157; sample_005: stated 130, actual 144). Readiness notes for the feature table are in `WRITEUP.md`.

## Summary of findings

- The regex and AI tables agreed on every cell except 4 blank-`sex` cells (my regex wrote `Unknown`, the AI left them blank).
- All 12 rows labeled mmol/L became biologically impossible after conversion (about 1,800-4,500 mg/dL), in both tables. The unit labels in the synthetic data appear to be assigned independently of the values.
- The AI warned about this in its chat message but still wrote the converted values in the CSV. It also said 15 values were impossible while listing only 12.
- Four dotted dates are ambiguous between month.day and day.month, and both approaches assumed month first.
- FASTA: the two tables agreed completely, but header lengths for sample_003 and sample_005 do not match the real sequences.

See `WRITEUP.md` for the full comparison, failure modes, time comparison, and which approach I would trust.

## AI use

AI tools were used for the Task 2 cleaning and to help write and explain the scripts and the write-up. Details are in `AI_USAGE.md`.