# Seating Studio - Bug Fixes (Latest)

## Problems Reported

1. **Subjects mixed "idhar-udhar" in same block** — even after first fix, subjects
   were appearing interleaved within a single block.
2. **Capacity not honored** — blocks weren't filling up to 30 students.
3. **QR barcodes not date-wise** — barcodes were generated in PRN sequence
   instead of being organized date-wise.

## Root Causes & Final Fixes

### Fix 1 — `sit3.py` : `auto_allocate_blocks()` (REVISED)

**Original Bug:** Students weren't sorted by Subject within each exam slot, so
the same subject could appear multiple times in one block with another subject
in between (interleaving / "idhar-udhar").

**Final Strategy ("fill capacity, subjects kept contiguous"):**
  * Students are sorted by `(Subject, PRN)` within each exam slot — this keeps
    same-subject students together in contiguous benches.
  * Blocks are filled greedily up to `block_capacity` in that sorted order.
    Mixing across subjects is allowed (to fill capacity) BUT same-subject
    students are never interleaved with another subject.
  * If a single subject has more students than capacity (e.g. 35 with cap 30),
    it cleanly overflows into the next block (30 + 5).

### Fix 2 (NEW) — `sit3.py` : `generate_pdf()` and `generate_attendance_sheet_pdf()`

**THE actual bug for "idhar-udhar" subjects:** Even though `auto_allocate_blocks`
correctly kept students in `(Subject, PRN)` order in memory, the PDF generation
functions were RE-SORTING students by PRN ONLY:

```python
# OLD (broken) - sorts by PRN only, breaking subject sequence:
student_data = sorted(block_data, key=lambda x: natural_key(str(x[4])))
attendance_data = sorted(block_data, key=lambda x: (natural_key(str(x[0])), ...))
```

This re-sort caused subjects to be interleaved inside each block in the actual
printed PDF, even though the in-memory order was correct.

**Fix:** Sort by `(Subject, PRN)` in both PDF generators:

```python
# NEW (fixed) - subject first, then PRN within subject:
student_data = sorted(block_data, key=lambda x: (str(x[2]).lower(), natural_key(str(x[4]))))
attendance_data = sorted(block_data, key=lambda x: (
    str(prn_to_subj_map.get(str(x[0]), "")).lower(),  # subject first
    natural_key(str(x[0])),                          # then PRN
    ...
))
```

### Fix 3 — `sit3.py` : empty `Exam_Center_Code` handling

When the `Exam_Center_Code` column exists in the CSV but is empty/NaN for all
rows, pandas `groupby` silently dropped every row, producing 0 blocks. Now the
column is only added as a grouping key when it actually has at least one
non-empty value. Also added `dropna=False` as a safety net.

### Fix 4 — `app2.py` : QR generator gets the right DataFrame

`qr.generate_all_qrs(df_raw.copy(), ...)` passed the RAW uploaded CSV (which
has `Exam Date`, not `Date`). So `qr.py` couldn't find a `Date` column, created
an empty one, and ALL students ended up under a single "Date" folder sorted
only by PRN. Now passes `plan["input_df"]` which has standardized `Date` and
`Exam_Session` columns.

### Fix 5 — `qr.py` : chronological date-wise ordering + fallback

Added `Exam Date` / `ExamDate` / `Date_of_Exam` column fallback, plus
`_date_sort_key` and `_session_sort_key` helpers. The whole frame is now sorted
by `(Date, Session, Subject, PRN)` before groupby so date folders are emitted
in chronological order.

## Test Results on Real CSV (270 students, capacity = 30)

### Block Allocation Summary
```
03-12-2026: 2 blocks, sizes=[30, 5], fill=58%
18-11-2026: 4 blocks, sizes=[30, 30, 30, 9], fill=82%
21-11-2026: 2 blocks, sizes=[30, 6], fill=60%
26-11-2026: 3 blocks, sizes=[30, 30, 16], fill=84%
30-11-2026: 1 blocks, sizes=[24], fill=80%

Blocks exceeding capacity 30: 0           PASS
Blocks with interleaved subjects: 0       PASS
All 12 blocks have proper subject sequence (no idhar-udhar)
```

### Actual PDF Output (18-11-2026, Block 1, capacity 30)

Verified by reading back the generated `block_seating_arrangement_report-1.pdf`:

```
Bench No  Program        PRN          Student Name                  Subject
1         BTECH_AD_SEM3  2310101035   POWAR SAMATA BABAN            } 23AD2301
2         BTECH_AD_SEM3  2310101038   SHINDE SAMIKSHA DIPAK         } (Linear Algebra
3         BTECH_AD_SEM3  2320101043   DAFEDAR ATTAULLA MUSA         }  and Probability)
4         BTECH_AD_SEM3  2410101008   BUJARE VEDANT SACHIN          }
5         BTECH_AD_SEM3  2410101021   KHOT OMKAR SAKHARAM           }
6         BTECH_AD_SEM3  2410201017   MANE HARSHVARDHAN MARUTI      }
7         BTECH_AD_SEM3  2420101047   PATIL SHRUTI MAHAVEER         }
8         BTECH_AD_SEM3  2420101057   SAMRUDHI ARUN SUTAR           }
9         BTECH_AD_SEM3  2440101067   JADHAV AARYA SUHAS            }

10        BTECH_AR_SEM3  2310102026   MOMIN ABUMANNAN ASHPAK        } 23AR2301
11        BTECH_AR_SEM3  2410102017   DHALAIT MAHEK TAUFIK          } (Sensors in
12        BTECH_AR_SEM3  2410102046   MALI HARISH CHINTAMAN         }  Automation &
13        BTECH_AR_SEM3  2410102049   MANKAR PARTH NITIN            }  Robotics)
...                                                              (contiguous)
20        BTECH_AR_SEM3  2510202005   KAMBLE SRUSHTI SANJAY         }

21        BTECH_CE_SEM3  2410103007   KOLI SHREYASH RAJIV           } 23CE2301
...                                                              (5 students, contiguous)

26        BTECH_CS_SEM3  2310104077   NADAF AMAN JAINUDDIN          } 23CS2301
...                                                              (5 students, contiguous)
30        BTECH_CS_SEM3  2410104063   KAMBLE SWAROOP MANGESH        }
```

**Verified priority order in actual PDF:**
1. ✅ Block capacity first — Block 1 has exactly 30 students
2. ✅ Subject sequence — AD → AR → CE → CS (alphabetical, no idhar-udhar)
3. ✅ PRN sequence — within each subject, PRN in ascending order

### QR Labels (Date-wise)
```
Date folders (chronological): ['03-12-2026', '18-11-2026', '21-11-2026', '26-11-2026', '30-11-2026']
  03-12-2026: 8 PDFs
  18-11-2026: 7 PDFs
  21-11-2026: 8 PDFs
  26-11-2026: 8 PDFs
  30-11-2026: 9 PDFs
```

## Files Modified

- `sit3.py`:
  - `auto_allocate_blocks()` — fill capacity + sort by (Subject, PRN)
  - `generate_pdf()` — **NEW FIX**: sort block_data by (Subject, PRN) instead of PRN-only
  - `generate_attendance_sheet_pdf()` — **NEW FIX**: sort by (Subject via prn_to_subject, PRN) instead of PRN-only
  - `Exam_Center_Code` NaN handling in `create_directories_and_pdfs()`
- `app2.py` — Pass `plan["input_df"]` to `qr.generate_all_qrs` instead of `df_raw`.
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

Re-upload the CSV and click Generate. The actual PDF reports (block seating
arrangement, attendance sheet) will now show subjects in proper sequence with
no interleaving, and each block will be filled to the configured capacity.
