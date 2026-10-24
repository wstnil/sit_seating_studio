# Seating Studio - Bug Fixes (23 Oct 2026)

## Problems Reported

1. **Subjects mixed in same block** — Within a single block, students from
   two different subjects were appearing interleaved (one subject code,
   then another in the same block).
2. **QR barcodes not date-wise** — Barcodes were being generated in PRN
   sequence all combined together, instead of being organized date-wise.

## Root Causes & Fixes

### Fix 1 — `sit3.py` : `auto_allocate_blocks()`
**Bug:** The old code filled blocks sequentially up to capacity. So if
Subject A had 25 students (capacity 30), the remaining 5 seats were filled
with Subject B's students → one block ended up with two subjects mixed.

**Fix:** When the subject changes, a NEW block is started immediately.
Remaining seats in the current block are left empty. Same-subject overflow
is still allowed (e.g. 35 students of one subject split into Block N
with 30 + Block N+1 with 5).

### Fix 2 — `sit3.py` : empty `Exam_Center_Code` handling
**Bug:** When the `Exam_Center_Code` column exists in the CSV but is
empty/NaN for all rows, pandas `groupby` silently dropped every row,
producing 0 blocks.

**Fix:** `Exam_Center_Code` is only included as a grouping key if it
actually has at least one non-empty value. Also added `dropna=False`
as a safety net.

### Fix 3 — `app2.py` : QR generator gets the right DataFrame
**Bug:** `qr.generate_all_qrs(df_raw.copy(), ...)` was passing the
RAW uploaded CSV. The raw CSV has a column called `Exam_Date`, not
`Date`. So `qr.py` couldn't find a `Date` column, silently created an
empty one, and ALL students ended up under a single "Date" folder
sorted only by PRN — exactly the "barcode not date-wise" complaint.

**Fix:** Pass `plan["input_df"]` (which already has standardized `Date`
and `Exam_Session` columns) instead of `df_raw`.

### Fix 4 — `qr.py` : chronological date-wise ordering + fallback
**Bug:** `groupby(... sort=False)` iterated groups in
"first-appearance" order, not chronological. Also no fallback for
the `Exam_Date` column name when running from CLI.

**Fix:**
- Added `Exam_Date` / `ExamDate` / `Date_of_Exam` column fallback.
- Added `_date_sort_key` and `_session_sort_key` helpers.
- Sort the whole frame by (Date, Session, Subject, PRN) before groupby
  so date folders are emitted in chronological order.

## Test Results

### Synthetic test (80 students, capacity 30)
- Subject A: 25 students → Block 1 (no mixing)
- Subject B: 20 students → Block 2 (no mixing)
- Subject C: 35 students → Block 3 (30) + Block 4 (5) — same subject split OK
- Result: 0 blocks mix multiple subjects ✓

### Real CSV test (274 students from `updated_student_list_with_blocks.csv`)
- 9 unique blocks allocated, 0 blocks mix multiple subjects ✓
- QR labels organized into 5 date folders in chronological order:
  `03-12-2026`, `18-11-2026`, `21-11-2026`, `26-11-2026`, `30-11-2026` ✓
- Each date folder has separate PDFs per (Session, Subject) ✓

## Files Modified

- `sit3.py` — `auto_allocate_blocks()` + Exam_Center_Code NaN handling in
  `create_directories_and_pdfs()` groupby.
- `app2.py` — Pass `plan["input_df"]` to `qr.generate_all_qrs` instead of
  `df_raw`.
- `qr.py` — `Exam_Date` fallback + chronological (Date, Session, Subject, PRN)
  sorting before groupby in `generate_all_qrs()`.

## How to Apply

Replace these 3 files in your project directory:
- `sit3.py`
- `app2.py`
- `qr.py`

`app.py`, `requirements.txt`, and `run_app.bat` are unchanged.

Then restart Streamlit:
```
python -m streamlit run app2.py
```
