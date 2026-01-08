import pdfplumber
import re
import os
from src.db.database import get_connection

# -------------------------------------------------
# PATHS
# -------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PDF_PATH = os.path.join(BASE_DIR, "data", "raw", "timetable.pdf")

# -------------------------------------------------
# DAY INDEX
# -------------------------------------------------
DAY_INDEX = {
    "Monday": 1,
    "Tuesday": 2,
    "Wednesday": 3,
    "Thursday": 4,
    "Friday": 5
}

# -------------------------------------------------
# TIME SLOTS
# -------------------------------------------------
TIME_SLOTS = [
    "08:30-09:30","09:30-10:30","10:30-11:30",
    "11:30-12:30","12:30-13:30",
    "13:30-14:30","14:30-15:30",
    "15:30-16:30","16:30-17:30","17:30-18:30"
]

# -------------------------------------------------
# LAB ROOM MAP
# -------------------------------------------------
LAB_ROOM_MAP = {
    "LAB1": "Lab-1",
    "LAB2": "Lab-2",
    "LAB3": "Lab-3",
    "LAB4": "Lab-4"
}

# -------------------------------------------------
# HELPERS
# -------------------------------------------------
def normalize_time(t):
    t = t.replace(".", ":").strip()
    h, m = map(int, t.split(":"))

    # PDF uses 1.30–6.30 for PM slots → convert to 13:30–18:30
    if h < 8:          # 1–7 means afternoon
        h += 12

    return f"{h:02d}:{m:02d}"


def get_division_index(division):
    return ord(division[-1]) - ord("A") + 1

DEFAULT_CLASSROOM = {
    "SE-Comp-A": "508",
    "SE-Comp-B": "508",
    "SE-Comp-C": "508",
    "SE-Comp-D": "508",
    "TE-Comp-A": "609",
    "TE-Comp-B": "609"
}

def get_default_classroom(division):
    if division not in DEFAULT_CLASSROOM:
        raise ValueError(f"Unknown division: {division}")
    return DEFAULT_CLASSROOM[division]



# -------------------------------------------------
# DB CONNECTION
# -------------------------------------------------
conn = get_connection()
cur = conn.cursor()

# Clean import
cur.execute("DELETE FROM timetable")
cur.execute("DELETE FROM sqlite_sequence WHERE name='timetable'")
conn.commit()

insert_sql = """
INSERT INTO timetable (
    division, division_index,
    day, day_index,
    slot_index, start_time, end_time,
    batch, subject, faculty,
    room, is_lab, category
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""

row_count = 0

# -------------------------------------------------
# PARSE PDF
# -------------------------------------------------
with pdfplumber.open(PDF_PATH) as pdf:
    for page_no, page in enumerate(pdf.pages):

        table = page.extract_table()
        if not table:
            continue

        DIVISION_BY_PAGE = {
            0: "SE-Comp-A",
            1: "SE-Comp-B",
            2: "SE-Comp-C",
            3: "SE-Comp-D",
            4: "TE-Comp-A",
            5: "TE-Comp-B"
        }

        if page_no not in DIVISION_BY_PAGE:
            continue  # skip unknown pages safely

        division = DIVISION_BY_PAGE[page_no]

        division_index = {
            "SE-Comp-A": 1,
            "SE-Comp-B": 2,
            "SE-Comp-C": 3,
            "SE-Comp-D": 4,
            "TE-Comp-A": 5,
            "TE-Comp-B": 6
        }[division]

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

                # 🔥 FIX: skip invalid / empty day headers
                if not day or day not in DAY_INDEX:
                    continue

                if not cell:
                    continue


                # 🔥 IMPORTANT FIX: split stacked entries
                entries = [e.strip() for e in cell.split("\n") if e.strip()]

                for entry in entries:
                    # Normalize separators: "\" → "/"
                    entry = entry.replace("\\", "/")

                    # Normalize extra spaces
                    entry = re.sub(r"\s+", " ", entry)

                    parts = [p.strip() for p in entry.split("/")]
                    # ---------------- CATEGORY B : LAB ----------------
                    if len(parts) == 4 and parts[3].upper().startswith("LAB"):
                        subject, batch, faculty, lab = parts
                        room = LAB_ROOM_MAP.get(lab.upper(), f"Lab-{lab.upper()}")

                        for s in (slot_index, slot_index + 1):
                            if s <= 10:
                                cur.execute(insert_sql, (
                                    division,
                                    division_index,
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
                                ))
                                row_count += 1
                        continue

                    # ---------------- CATEGORY C : ELECTIVE ----------------
                    if len(parts) == 3:
                        subject, faculty, room = parts
                        cur.execute(insert_sql, (
                            division,
                            division_index,
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
                        ))
                        row_count += 1
                        continue

                    # ---------------- CATEGORY A : THEORY ----------------
                    subject = parts[0]
                    faculty = parts[1] if len(parts) > 1 else "Unknown"

                    cur.execute(insert_sql, (
                        division,
                        division_index,
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
                    ))
                    row_count += 1

conn.commit()
conn.close()

print(f"PDF → DB completed successfully. Rows inserted: {row_count}")
