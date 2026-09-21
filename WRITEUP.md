# Lab 3 Write-Up: Regex vs. AI-Assisted Cleaning of messy_samples.csv

Course: PUBH 4201 (undergraduate), so I cleaned one file: messy_samples.csv (60 clinical sample records).

## 1. What I did

Regex approach: I wrote clean_samples.py (Python, using only the built-in re, csv, and datetime modules). I built it one column at a time and checked each piece against the raw rows before moving on. Anything a pattern did not recognize is printed as a PROBLEM line instead of being guessed at. Output: clean_samples.csv.

AI approach: I uploaded the same messy_samples.csv to a fresh AI chat with no context from my regex work, and gave it one prompt (saved in AI_USAGE.md) with the same target formats my script uses. I deliberately did not tell it about the glucose unit problem I had found, so I could see what it did on its own. Output: ai_clean_samples.csv.

Comparison: I wrote compare.py, which lines up the two tables by sample_id and lists every cell where they differ (comparison_diffs.csv).

What was messy in the file:
- sample_id: S0001 vs s-0003
- patient_name: a few ALL-CAPS names
- dob: four date styles (07/09/1962, 1997-12-02, 21-Jun-1997, 11.24.53)
- sex: F, f, Female, M, m, Male, U, unknown, and blank
- enrollment_site: Site A, SITE-A, site_a, siteB, "Site  C" (two spaces), "Site C " (trailing space)
- glucose_value: N/A, and values with a trailing * (for example 112.3*)
- glucose_unit: mg/dL, mg/dl, MG/DL, and mmol/L

Setup note: messy_samples.csv was not in the course repo (only generate_data.py, the FASTA file, and SOURCE.md were). I regenerated it by running the given seeded generate_data.py from inside my own data folder. I checked that the regenerated messy_sequences.fasta was identical to the instructor's (diff printed nothing), so the seed reproduced the data as intended.

## 2. Where the two approaches agreed

Both tables had 60 rows and the AI skipped none (its last row was S0060). Across all 60 rows the two tables agreed on every cell of patient_name, dob, enrollment_site, glucose_mg_dl, and notes. That is 56 of 60 rows fully identical. The cleaned formats matched: IDs like S0001, names like "A. Smith", dates as YYYY-MM-DD, sites as Site A/B/C, and glucose in mg/dL.

Both handled the same judgment calls the same way:
- Slash dates (07/09/1962) were read as month/day/year. 12/16/1974 proves this, because there is no 16th month.
- Dotted dates (11.24.53) were read as month.day.year, and 53 became 1953, not 2053.
- N/A glucose became blank (kept as missing, not dropped).
- The trailing * on glucose values (S0032, S0043) was removed.
- ALL-CAPS names were fixed to normal capitalization.

## 3. Where they disagreed

compare.py found exactly 4 disagreements, all in the sex column: S0013, S0018, S0037, and S0046. These rows have a blank sex value. My regex wrote "Unknown"; the AI left them blank and only turned the entries that actually said "unknown" or "U" into "Unknown".

This is a difference in assumptions, not a mistake by either side. My choice treats "never recorded" and "recorded as unknown" as the same thing. The AI's choice keeps them separate, which is arguably more honest, because a blank could mean the field was never filled in and "unknown" could mean someone checked and could not tell. I would document whichever choice I made, which is why it is listed in AI_USAGE.md.

The two tools also used different two-digit-year cutoffs. My script maps 50-99 to 1950-1999 and 00-49 to 2000-2049. The AI said it switches at 26 (26 or below became 20xx, higher became 19xx). These only give different answers for years 27-49. I checked all 14 dotted-date rows with grep, and the two-digit years were 53, 73, 02, 64, 60, 56, 12, 95, 98, 18, 98, 09, 89, and 06, so none fell in that range. That is why compare.py found no date disagreements. It was luck of the data, not evidence that the two cutoffs are equivalent.

## 4. Failure modes

### Failure mode 1: the mmol/L glucose rows (both approaches wrong)

12 rows are labeled mmol/L (for example S0006, S0011, S0014, S0015, S0016, S0017, S0024, S0033, S0035, S0038, S0039, S0046). I was asked to convert to mg/dL, so my script multiplied by 18.016. Every one of those 12 rows became biologically impossible. My flag counts showed converted_from_mmol = 12 and implausible_after_conversion = 12, meaning 12 of 12. For example, S0006 was 141.2 "mmol/L", which became 2543.9 mg/dL, and S0017 was 249.2, which became 4489.6. The original numbers (about 99 to 249) look like normal mg/dL readings, not mmol/L (normal glucose in mmol/L is roughly 4-8).

Why it happened: reading the instructor's generator script, the unit label is chosen at random, independent of the glucose value. So a normal mg/dL-range number can end up labeled mmol/L. My script did exactly what the lab asked, ran without any error, and still produced confident, wrong numbers. This is the Week 4 lesson that a pattern (or a rule) can look right and be quietly wrong. Regex can match text, but it cannot know that 141 mmol/L is impossible.

How each approach behaved:
- Regex: converted the values, but my script added a plausibility check (values outside 20-600 mg/dL are flagged), so the problem is visible in the glucose_flag column. I also kept the original value and unit in separate columns so every change can be traced back.
- AI: also converted the values (its CSV shows 2543.9 for S0006, the same as mine), with no flag column, but its chat message warned that the mmol/L labels were probably wrong and offered to regenerate the file with the original values if I confirmed. It noticed the problem on its own; the regex script only found it because I wrote the check.

### Failure mode 2: the AI's numbers did not match its own list

The AI's message said 15 of the converted values were physiologically impossible, but it listed only 12 sample IDs (and my regex flagged exactly 12). It stated a confident count that did not match its own evidence. Nothing errored; the mistake was only visible because I had my own count to check it against. This is the "confident, wrong answer" failure that Week 4 describes for AI extraction, as opposed to regex, which tends to fail loudly with an error or a PROBLEM line.

### Failure mode 3: ambiguous dates that neither approach can verify

Slash dates like 07/09/1962 are ambiguous in the same way (July 9 or September 7?). I resolved that format by evidence (12/16/1974 can only be month/day), but the dotted format has four rows where both numbers could be a month, so the day and month could be swapped: s-0034 (06.07.12), S0037 (09.06.98), S0058 (02.08.89), and S0060 (02.09.06). Both tools assumed month first and agreed with each other, but agreement is not proof. The AI itself said 09.06.98 could also be read as DD.MM. In this dataset the generator's date format list includes a month.day.two-digit-year format, so month-first is very likely right. With real data I would have no such way to check, and I would need to ask whoever collected the data.

A related risk is the two-digit year rule. Both cutoffs (50 for mine, 26 for the AI's) are assumptions. They work here only because the generator produces birth dates from 1950 to about 2018, which I know from reading the generator, and I could not know that with real data.

### Agreement does not mean correct

The 12 impossible glucose values are the clearest example: two independent methods produced identical wrong numbers. Comparing two tools only finds where their assumptions differ, not where they share the same wrong assumption.

## 5. Time and effort

- Regex: it took me about 3-4 hours from setup to a finished script, and that was with step-by-step help from Claude. Some of that time went to setup problems (the missing CSV, a long terminal paste that got stuck in "heredoc" mode and had to be replaced with a text editor). I also had to learn regex tokens (\d, \w, [sS], -?, {n}, fullmatch) as I went. Fixing a single pattern was quick, but the total effort was much higher than the AI.
- AI: about 1 minute from upload to output, plus a few minutes to save it as a file.

So the AI was far faster to get a first result. But the regex script is a reusable, testable file that I understand line by line, and it produced information the AI's CSV did not (flag columns, original values, flag counts).

## 6. Which I would trust for a real dataset

For a real dataset I would not trust either one alone.

- I would use regex for well-defined fields (IDs, dates, categories) because it is deterministic, gives the same output every time, can be re-run on new data, and reports what it does not recognize. Its weakness is that it only knows the patterns I gave it, so I need to test against messy examples, not just the first rows.
- I would use the AI as a fast first pass and, more importantly, as a reviewer. It caught the impossible glucose values without being told to look, which my regex only did because I added a check. Its weaknesses are that it can state wrong facts confidently (the 15 vs 12 count), its output is not guaranteed to be the same each time, and the CSV had no audit trail of what it changed.
- In both cases I would add a plausibility check on the numbers and a human check on the flagged rows and ambiguous dates, and I would keep the original values next to the cleaned ones.

Limitations: I could see only part of the file when I first wrote the patterns (the first 14 rows), so the script prints PROBLEM for anything unrecognized. It printed none across all 60 rows, but I only have the two tools to compare with, not an answer key, so I cannot be sure that every value agreed on is correct.