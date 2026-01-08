import pandas as pd
import os
from src.db.database import get_connection

# -------------------------------------------------
# PATH RESOLUTION
# -------------------------------------------------
BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)

EXCEL_PATH = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "timetable_expanded.xlsx"
)

print("Reading Excel from:", EXCEL_PATH)

if not os.path.exists(EXCEL_PATH):
    raise FileNotFoundError(f"Excel file not found: {EXCEL_PATH}")

# -------------------------------------------------
# LOAD EXCEL
# -------------------------------------------------
df = pd.read_excel(EXCEL_PATH)
df.columns = df.columns.str.strip()  # ✅ important

# -------------------------------------------------
# HELPERS (DO NOT TRUST EXCEL BLINDLY)
# -------------------------------------------------
def get_division_index(division):
    # SE-Comp-A → 1, SE-Comp-B → 2, ...
    return ord(division.strip()[-1]) - ord("A") + 1

DAY_INDEX = {
    "Monday": 1,
    "Tuesday": 2,
    "Wednesday": 3,
    "Thursday": 4,
    "Friday": 5
}

# -------------------------------------------------
# DB CONNECTION
# -------------------------------------------------
conn = get_connection()
cur = conn.cursor()

# -------------------------------------------------
# RESET TABLE
# -------------------------------------------------
cur.execute("DELETE FROM timetable")
cur.execute("DELETE FROM sqlite_sequence WHERE name='timetable'")
conn.commit()

# -------------------------------------------------
# INSERT ROWS
# -------------------------------------------------
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

for _, r in df.iterrows():

    # -------- Mandatory fields --------
    if pd.isna(r.get("Division")) or pd.isna(r.get("Day")) or pd.isna(r.get("Slot")):
        continue

    division = str(r["Division"]).strip()
    day = str(r["Day"]).strip()

    # -------- Safe dynamic indexes --------
    division_index = (
        int(r["Division_Index"])
        if "Division_Index" in df.columns and pd.notna(r.get("Division_Index"))
        else get_division_index(division)
    )

    day_index = (
        int(r["Day_Index"])
        if "Day_Index" in df.columns and pd.notna(r.get("Day_Index"))
        else DAY_INDEX.get(day, 0)
    )

    # -------- Safe defaults --------
    batch = r["Batch"] if pd.notna(r.get("Batch")) else "Full"
    faculty = r["Faculty"] if pd.notna(r.get("Faculty")) else "Unknown"
    room = r["Room"] if pd.notna(r.get("Room")) else "Classroom"

    cur.execute(insert_sql, (
        division,
        division_index,
        day,
        day_index,
        int(r["Slot"]),
        str(r["Start"]),
        str(r["End"]),
        str(batch).strip(),
        str(r["Subject"]).strip(),
        str(faculty).strip(),
        str(room).strip(),
        int(r["Is_Lab"]),
        str(r["Category"]).strip()
    ))

    row_count += 1

conn.commit()
conn.close()

print(f"Excel → DB completed successfully. Rows inserted: {row_count}")
