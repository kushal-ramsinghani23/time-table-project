import pdfplumber
import pandas as pd
import re
import os

# -------------------------------------------------
# PATHS
# -------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PDF_PATH = os.path.join(BASE_DIR, "data", "raw", "timetable.pdf")
OUT_PATH = os.path.join(BASE_DIR, "data", "processed", "timetable_expanded.xlsx")

# -------------------------------------------------
# DAY INDEX (ORDERING)
# -------------------------------------------------
DAY_INDEX = {
    "Monday": 1,
    "Tuesday": 2,
    "Wednesday": 3,
    "Thursday": 4,
    "Friday": 5
}

# -------------------------------------------------
# LAB NAME → ROOM MAP
# -------------------------------------------------
LAB_ROOM_MAP = {
    "LAB1": "Lab-LAB1",
    "LAB2": "Lab-LAB2",
    "LAB3": "Lab-LAB3",
    "LAB4": "Lab-LAB4"
}

# -------------------------------------------------
# FACULTY NORMALIZATION
# -------------------------------------------------
FACULTY_MAP = {
    "JSR": "JS",
    "JS": "JS",
    "NR": "NR",
    "KKD": "KKD"
}

# -------------------------------------------------
# TIME SLOTS (CANONICAL)
# -------------------------------------------------
TIME_SLOTS = [
    "08:30-09:30","09:30-10:30","10:30-11:30",
    "11:30-12:30","12:30-13:30",
    "13:30-14:30","14:30-15:30",
    "15:30-16:30","16:30-17:30","17:30-18:30"
]

# -------------------------------------------------
# HELPERS
# -------------------------------------------------
def normalize_time(t):
    t = t.replace(".", ":")
    h, m = t.split(":")
    return f"{int(h):02d}:{m}"

def normalize_faculty(name):
    return FACULTY_MAP.get(name.strip().upper(), name.strip().upper())

def get_division_index(division):
    # SE-Comp-A → 1, SE-Comp-E → 5
    return ord(division[-1]) - ord("A") + 1

def get_default_classroom(division):
    # SE-Comp-A → CR-A, SE-Comp-E → CR-E
    return f"CR-{division[-1]}"

# -------------------------------------------------
# PARSE PDF
# -------------------------------------------------
rows = []

with pdfplumber.open(PDF_PATH) as pdf:
    for page_no, page in enumerate(pdf.pages):

        table = page.extract_table()
        if not table:
            continue

        division = f"SE-Comp-{chr(65 + page_no)}"
        days = table[0][1:]

        for r in table[1:]:
            if not r[0]:
                continue

            match = re.search(
                r"(\d{1,2}[.:]\d{2})\s*[-–]\s*(\d{1,2}[.:]\d{2})",
                r[0]
            )
            if not match:
                continue

            start = normalize_time(match.group(1))
            end = normalize_time(match.group(2))
            slot_key = f"{start}-{end}"

            if slot_key not in TIME_SLOTS:
                continue

            slot_index = TIME_SLOTS.index(slot_key) + 1

            for day, cell in zip(days, r[1:]):
                if not cell:
                    continue

                parts = [p.strip() for p in cell.replace("\n", " ").split("/")]

                # ---------------- CATEGORY B : LAB ----------------
                if len(parts) == 4 and parts[3].upper().startswith("LAB"):
                    subject, batch, faculty, lab = parts
                    faculty = normalize_faculty(faculty)
                    room = LAB_ROOM_MAP.get(lab.upper(), f"Lab-{lab.upper()}")

                    for s in (slot_index, slot_index + 1):
                        if s <= 10:
                            rows.append([
                                division,
                                get_division_index(division),
                                day,
                                DAY_INDEX[day],
                                s,
                                start,
                                end,
                                batch,
                                subject,
                                faculty,
                                room,
                                1,
                                "B"
                            ])
                    continue

                # ---------------- CATEGORY C : ELECTIVE ----------------
                if len(parts) == 3:
                    subject, faculty, room = parts
                    faculty = normalize_faculty(faculty)

                    rows.append([
                        division,
                        get_division_index(division),
                        day,
                        DAY_INDEX[day],
                        slot_index,
                        start,
                        end,
                        "Elective",
                        subject,
                        faculty,
                        room,
                        0,
                        "C"
                    ])
                    continue

                # ---------------- CATEGORY A : THEORY ----------------
                subject = parts[0]
                faculty = normalize_faculty(parts[1]) if len(parts) > 1 else "Unknown"

                rows.append([
                    division,
                    get_division_index(division),
                    day,
                    DAY_INDEX[day],
                    slot_index,
                    start,
                    end,
                    "Full",
                    subject,
                    faculty,
                    get_default_classroom(division),
                    0,
                    "A"
                ])

# -------------------------------------------------
# CREATE EXCEL
# -------------------------------------------------
df = pd.DataFrame(rows, columns=[
    "Division","Division_Index",
    "Day","Day_Index",
    "Slot","Start","End",
    "Batch","Subject","Faculty",
    "Room","Is_Lab","Category"
])

os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)

try:
    df.to_excel(OUT_PATH, index=False)
except PermissionError:
    df.to_excel(OUT_PATH.replace(".xlsx", "_new.xlsx"), index=False)

print("PDF → Excel completed successfully")
