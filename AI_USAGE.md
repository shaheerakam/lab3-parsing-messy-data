# AI Usage

## Task 1: Regex script (clean_samples.py)
Used Claude to help write and explain the regex patterns and script, step by step.
I ran each piece, checked the output against the raw rows, and tested for problems.
Assumptions I accepted: two-digit years 50-99 = 1950-1999, 00-49 = 2000-2049;
slash and dotted dates are month/day/year; blank sex = Unknown; all glucose converted to mg/dL.

## Task 2: AI-assisted cleaning
Tool used: Claude Sonnet 5
Time spent: about 1 minute

### Prompt 1
I have a messy clinical sample file (attached: messy_samples.csv, 60 records). Please clean it and give me the result as CSV text I can copy. Output these columns: sample_id, patient_name, dob, sex, enrollment_site, glucose_mg_dl, notes.

Rules:
- sample_id like S0001
- patient_name like "A. Smith"
- dob as YYYY-MM-DD
- sex as M, F, or Unknown
- enrollment_site as Site A, Site B, or Site C
- glucose in mg/dL (convert from mmol/L if needed)
- leave missing values blank
- keep the notes column

Output all 60 rows.

### The AI's chat message with the CSV
Please check the glucose values for the mmol/L rows. I converted them as you asked (x 18.016), but 15 of the resulting values are physiologically impossible, from about 1,350 to 4,490 mg/dL (S0006, S0011, S0014, S0015, S0016, S0017, S0024, S0033, S0035, S0038, S0039, S0046). The original numbers on those rows (75 to 250) look like normal mg/dL readings, so the "mmol/L" labels are probably wrong. If so, those rows should keep their original values. I can regenerate the file that way if you confirm.

Other judgment calls:
- Slash dates: I read 07/09/1962-style dates as MM/DD/YYYY. Several others in the file (like 12/16/1974) can only be read that way.
- Dotted dates: MM.DD.YY dates with two-digit years 26 or below became 20xx, and higher years became 19xx. For example, 05.30.02 became 2002 and 11.24.53 became 1953. Some of these dates, such as 09.06.98, could also be read as DD.MM, so check them if that format is possible.
- Blank sex: Rows with no sex value (S0013, S0018, S0037, S0046) stay blank. Only entries that said "unknown" or "U" became Unknown.
- Glucose values: N/A (S0012, S0056) became blank. The trailing * on 112.3 and 223.1 (S0032, S0043) was dropped, and the file gave no explanation for it.
- Names: All-caps surnames were fixed (J. KIM became J. Kim, S. DAVIS became S. Davis).

### My observations
- The AI warned in chat that the mmol/L conversions gave impossible values, but still wrote the converted numbers in the CSV.
- It said 15 values were impossible but listed only 12 IDs. My regex flagged exactly 12.
- It left blank sex values blank, while my regex wrote "Unknown" (4 disagreements: S0013, S0018, S0037, S0046).
- Both approaches assumed month-first for ambiguous dotted dates (for example 09.06.98).

## Write-up
Used Claude to lengthen and include higher detail into WRITEUP.md based on my original writing and directions. I reviewed it against my outputs and edited it accordingly.