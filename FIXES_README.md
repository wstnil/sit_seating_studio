# Seating Studio - Bug Fixes (Latest)

## Problems Reported & Fixed

1. ~~Subjects mixed "idhar-udhar" in same block~~ — FIXED
2. ~~Capacity not honored~~ — FIXED
3. ~~QR barcodes not date-wise~~ — FIXED
4. ~~Course codes invisible in heading~~ — FIXED
5. **NEW: Show Course Code + Course Name as ONE merged line** — FIXED (this update)

## The Latest Fix — Merged Course Heading Line

### User Request

> "Course name mai (course code - course name) aisaa krr, separate separate nko"

= Show each course as a single paired string `"code - name"` instead of having
two separate "Course Name:" and "Course Code:" heading lines.

### Before

The block seating arrangement PDF heading had TWO separate multi_cell lines:

```
Course Name: Linear Algebra and Probability, Sensors in Automation and Robotics, ...
Course Code: 23AD2301, 23AR2301, 23CE2301, 23CS2301
```

The user found this redundant and asked for them to be merged into one line
showing each course as a `(code - name)` pair.

### After

Now there is a SINGLE heading line:

```
Course: 23AD2301 - Linear Algebra and Probability, 23AR2301 - Sensors in Automation
        and Robotics, 23CE2301 - Engineering Mathematics -III, 23CS2301 - Mathematics
        for Computer Science
```

### Implementation

In `sit3.py :: generate_pdf()`:

1. Instead of building two separate lists `codes[]` and `titles[]`, build a
   single list of `(code, title)` pairs (with proper de-duplication).
2. Build a single `course_combined` string: `"code1 - title1, code2 - title2, ..."`.
3. Replace the two `multi_cell` calls with one:

```python
# OLD (two separate lines):
pdf.multi_cell(table_width, 7, f"Course Name: {course_name}", border=1, align="C", ...)
pdf.multi_cell(table_width, 7, f"Course Code: {course_code}", border=1, align="C", ...)

# NEW (one merged line):
pdf.multi_cell(table_width, 7, f"Course: {course_combined}", border=1, align="C",
               new_x=XPos.LMARGIN, new_y=YPos.NEXT)
```

### Verification

Visually verified using a Vision-Language Model on the rendered PDF preview:

```
1. Sharad Institute of Technology College of Engineering
2. (An Autonomous Institute)
3. Winter Semester Examination 2026 Final Year B.Tech (sem - VII )
4. Block Number: 1 | Room No: ___________
5. Course: 23AD2301 - Linear Algebra and Probability, 23AR2301 - Sensors
   in Automation and Robotics, 23CE2301 - Engineering Mathematics-III,
   23CS2301 - Mathematics for Computer Science     ← ONE MERGED LINE
6. Date and Time: 18-11-2026 10.00 AM - 12.00 PM
7. Institute Code: EN6317 | Institute Name: Sharad Institute of Technology
```

VLM confirmed: **"There is ONE merged 'Course:' line showing each course as
'code - name' pairs. There are no separate 'Course Name:' and 'Course Code:'
lines in this heading section."**

All 12 block PDFs verified — every block now has the merged `Course:` line.

## All Earlier Fixes (Still In Place)

### Block Allocation Strategy — `auto_allocate_blocks()`

Sort students by `(Subject, PRN)` within each exam slot. Fill blocks greedily
up to capacity. Same-subject students stay contiguous; mixing across subjects
is allowed (to fill capacity) but never interleaved.

### PDF Sort Order — `generate_pdf()` and `generate_attendance_sheet_pdf()`

Sort `block_data` by `(Subject, PRN)` instead of PRN-only. This was the
actual fix for the original "idhar-udhar" complaint.

### Invisible "Course Code:" Heading (previous fix)

FPDF2 v2.8.5's `multi_cell()` default `new_x=XPos.RIGHT` leaves the cursor at
the right edge of a full-width cell, causing the next `multi_cell()` to render
off-page. Fixed by passing `new_x=XPos.LMARGIN, new_y=YPos.NEXT`.

### Empty `Exam_Center_Code` Handling

When the column exists but all values are NaN/empty, skip it as a grouping
key (otherwise `groupby` drops every row → 0 blocks).

### QR Labels Date-wise

- `app2.py` now passes `plan["input_df"]` (with standardized `Date` column)
  to `qr.generate_all_qrs` instead of `df_raw`.
- `qr.py` adds `Exam Date` column fallback and sorts the whole frame by
  `(Date, Session, Subject, PRN)` before groupby, so date folders are emitted
  in chronological order.

## Files Modified

- `sit3.py`:
  - **NEW**: `generate_pdf()` now builds a single merged `course_combined`
    string and renders ONE "Course:" line instead of two separate
    "Course Name:" / "Course Code:" lines.
  - `multi_cell` calls use `new_x=XPos.LMARGIN, new_y=YPos.NEXT` to fix
    invisible Course Code heading.
  - Same fix in `generate_seat_number_summary_pdf()`.
  - Added `from fpdf import FPDF, XPos, YPos` import.
  - `auto_allocate_blocks()` — fill capacity + sort by (Subject, PRN).
  - `generate_pdf()` — sort `block_data` by (Subject, PRN).
  - `generate_attendance_sheet_pdf()` — sort by (Subject via prn_to_subject, PRN).
  - `Exam_Center_Code` NaN handling in `create_directories_and_pdfs()`.
- `app2.py` — Pass `plan["input_df"]` to `qr.generate_all_qrs`.
- `qr.py` — `Exam Date` fallback + chronological (Date, Session, Subject, PRN) sorting.

## How to Apply

Replace these 3 files in your project directory:
- `sit3.py`
- `app2.py`
- `qr.py`

Then restart Streamlit:
```
python -m streamlit run app2.py
```

Re-upload the CSV and click Generate. The block seating arrangement report's
heading will now show ONE merged `Course: code1 - name1, code2 - name2, ...`
line instead of two separate Course Code and Course Name lines.
