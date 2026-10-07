"""
QR Code Label Generator (FINAL – Dynamic Name Font)
- A4 PDF, 2 columns x 14 rows
- Label size: 96mm x 20mm
- Dynamic font size for long student names
- QR code on right
- Date-wise folders
- PDF name: SubjectCode_SubjectName.pdf
"""

import os
import re
from io import BytesIO
from datetime import datetime

import pandas as pd
import qrcode
from fpdf import FPDF
import sit3

# =============================================================================
# LAYOUT CONSTANTS
from typing import Tuple
# =============================================================================
PAGE_MARGIN_LEFT = 5.0
PAGE_MARGIN_TOP = 2.0

COLUMNS_PER_PAGE = 2
ROWS_PER_PAGE = 14
LABELS_PER_PAGE = COLUMNS_PER_PAGE * ROWS_PER_PAGE

LABEL_WIDTH = 96.0
LABEL_HEIGHT = 20.0

HORIZONTAL_GAP = 4.0
VERTICAL_GAP = 0.8

INNER_PADDING_X = 2.0
SPACE_BETWEEN_TEXT_AND_QR = 0.8
QR_LEFT_SHIFT = 9.0

TEXT_VERTICAL_SHIFT = 0.2

QR_SIZE = 13.0

# Text control
TEXT_SIZE = 7
NAME_MIN_FONT = 5
TEXT_LINE_HEIGHT = 4.2

TEXT_MAX_NAME = 45
TEXT_MAX_COURSE = 30

# =============================================================================
# PATHS
# =============================================================================
DEFAULT_INPUT_FILE = r"demoqr.xlsx"
OUTPUT_DIR = r"output"

# =============================================================================
# PDF CLASS
# =============================================================================
class PDF(FPDF):
    def header(self): pass
    def footer(self): pass

# =============================================================================
# UTILITIES
# =============================================================================
def safe_filename(text: str) -> str:
    return re.sub(r'[<>:"/\\|?*]', "_", str(text)).strip()

def truncate_text(text: str, max_len: int) -> str:
    text = str(text).strip()
    if len(text) > max_len:
        return text[:max_len - 3] + "..."
    return text


def parse_subject_details(value: str) -> tuple[str, str, str]:
    parts = [part.strip() for part in str(value or "").split("/") if part.strip()]
    if not parts:
        return "", "", ""
    if len(parts) >= 3:
        return parts[0], parts[1], " / ".join(parts[2:])
    return parts[0], "", parts[1] if len(parts) == 2 else ""


def generate_qr_code_stream(data: str) -> BytesIO:
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(str(data))
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf

# =============================================================================
# POSITION CALCULATION
# =============================================================================
def calculate_label_position(i: int) -> Tuple[int, int, float, float]:
    row = i // COLUMNS_PER_PAGE
    col = i % COLUMNS_PER_PAGE
    x = PAGE_MARGIN_LEFT + col * (LABEL_WIDTH + HORIZONTAL_GAP)
    y = PAGE_MARGIN_TOP + row * (LABEL_HEIGHT + VERTICAL_GAP)
    return row, col, x, y

# =============================================================================
# ADD SINGLE LABEL (DYNAMIC NAME FONT)
# =============================================================================
def add_label_to_pdf(pdf: PDF, student: dict, x: float, y: float):
    # QR position
    qr_x = x + LABEL_WIDTH - INNER_PADDING_X - QR_SIZE - QR_LEFT_SHIFT
    qr_y = y + (LABEL_HEIGHT - QR_SIZE) / 2

    # Text area width
    text_area_width = qr_x - (x + INNER_PADDING_X) - SPACE_BETWEEN_TEXT_AND_QR
    text_x = x + INNER_PADDING_X
    text_y = y + (LABEL_HEIGHT - 4 * TEXT_LINE_HEIGHT) / 2 + TEXT_VERTICAL_SHIFT

    name_text = truncate_text(student.get("Name", ""), TEXT_MAX_NAME)
    if len(name_text) > 28:
        name_font = max(TEXT_SIZE - 2, NAME_MIN_FONT)
    elif len(name_text) > 20:
        name_font = TEXT_SIZE - 1
    else:
        name_font = TEXT_SIZE

    lines = [
        (name_text, name_font),
        (str(student.get("PRN", "")), TEXT_SIZE),
        (str(student.get("Course", "")), TEXT_SIZE),
        (str(student.get("Random_Digit_Number", "")), TEXT_SIZE),
    ]

    for index, (text, font_size) in enumerate(lines):
        pdf.set_font("Times", "B", font_size)
        while font_size > NAME_MIN_FONT and pdf.get_string_width(text) > text_area_width:
            font_size = max(NAME_MIN_FONT, font_size - 0.5)
            pdf.set_font("Times", "B", font_size)
        pdf.set_xy(text_x, text_y + index * TEXT_LINE_HEIGHT)
        pdf.cell(text_area_width, TEXT_LINE_HEIGHT, text)

    # -------- QR CODE --------
    qr_buf = generate_qr_code_stream(student.get("Random_Digit_Number", ""))
    pdf.image(qr_buf, x=qr_x, y=qr_y, w=QR_SIZE, h=QR_SIZE)

# =============================================================================
# LOAD DATA
# =============================================================================
def load_data_file(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(path)

    df = pd.read_excel(path)

    required = ["PRN", "Name", "Course", "Subject Name", "Random_Digit_Number", "Date"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    df = df.fillna("")
    df["Date"] = pd.to_datetime(df["Date"]).dt.date
    df["Subject Code"] = df["Course"]

    return df

# =============================================================================
# PDF GENERATION
# =============================================================================
def generate_pdf_for_subject(subject_code, subject_name, group, date_folder):
    pdf = PDF("P", "mm", "A4")
    pdf.set_auto_page_break(False)
    pdf.add_page()

    count = 0
    for _, row in group.iterrows():
        if count > 0 and count % LABELS_PER_PAGE == 0:
            pdf.add_page()

        _, _, x, y = calculate_label_position(count % LABELS_PER_PAGE)
        add_label_to_pdf(pdf, row.to_dict(), x, y)
        count += 1

    filename = f"{safe_filename(subject_code)}_{safe_filename(subject_name)}.pdf"
    pdf.output(os.path.join(date_folder, filename))
    print(f"Generated: {filename}")

def generate_all_qrs(data: pd.DataFrame, output_dir: str, qr_column: str) -> None:
    if qr_column not in data.columns:
        raise ValueError(f"QR code field not found in dataset: {qr_column}")

    labels = data.fillna("").copy()
    for column in ("Date", "Name", "PRN", "Course", "Subject"):
        if column not in labels.columns:
            labels[column] = ""

    session_column = next(
        (column for column in ("Exam_Session", "Session") if column in labels.columns),
        None,
    )
    labels["Session"] = (
        labels[session_column].fillna("").astype(str).str.strip()
        if session_column is not None
        else ""
    )
    labels["Date"] = labels["Date"].map(sit3.normalize_exam_date)
    labels["QR_Value"] = labels[qr_column].astype(str)
    subject_details = labels["Subject"].map(parse_subject_details)
    labels["Subject Code"] = subject_details.map(lambda details: details[0] or "Subject")
    labels["Pattern"] = subject_details.map(lambda details: details[1])
    labels["Subject Name"] = subject_details.map(lambda details: details[2])
    labels["Course"] = [
        details[0] or course
        for details, course in zip(subject_details, labels["Course"].astype(str).str.strip())
    ]
    labels["Random_Digit_Number"] = labels["QR_Value"]

    for (exam_date, exam_session, subject_code, subject_name), group in labels.groupby(
        ["Date", "Session", "Subject Code", "Subject Name"], sort=False, dropna=False
    ):
        session_folder = sit3.format_session_label(exam_session) if exam_session else "Session"
        label_folder = os.path.join(
            output_dir,
            "QR Labels",
            safe_filename(exam_date or "Date"),
            safe_filename(session_folder),
        )
        os.makedirs(label_folder, exist_ok=True)
        generate_pdf_for_subject(subject_code, subject_name, group, label_folder)

# =============================================================================
# MAIN
# =============================================================================
def main():
    data = load_data_file(DEFAULT_INPUT_FILE)
    data = data.sort_values(by="PRN")

    for exam_date, date_group in data.groupby("Date"):
        date_folder = os.path.join(OUTPUT_DIR, exam_date.strftime("%Y-%m-%d"))
        os.makedirs(date_folder, exist_ok=True)

        for (sub_code, sub_name), grp in date_group.groupby(["Subject Code", "Subject Name"]):
            generate_pdf_for_subject(sub_code, sub_name, grp, date_folder)

    print("✅ ALL PDFs GENERATED SUCCESSFULLY")

if __name__ == "__main__":
    main()
