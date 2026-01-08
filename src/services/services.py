from src.db.database import get_connection

# -------------------------------------------------
# 1️⃣ FACULTY TIMETABLE (PARTIAL MATCH, ORDERED)
# -------------------------------------------------
def get_faculty_timetable(faculty):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            day,
            slot_index,
            start_time,
            end_time,
            division,
            batch,
            subject,
            room,
            is_lab,
            category
        FROM timetable
        WHERE LOWER(faculty) LIKE LOWER(?)
        ORDER BY division_index, day_index, slot_index
    """, (f"%{faculty.strip()}%",))

    rows = cur.fetchall()
    conn.close()
    return rows


# -------------------------------------------------
# 2️⃣ DIVISION TIMETABLE
# -------------------------------------------------
def get_division_timetable(division):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            day,
            slot_index,
            start_time,
            end_time,
            subject,
            faculty,
            room,
            category
        FROM timetable
        WHERE division = ?
        ORDER BY day_index, slot_index
    """, (division.strip(),))

    rows = cur.fetchall()
    conn.close()
    return rows


# -------------------------------------------------
# 3️⃣ LAB OCCUPIED (STRICT LAB MATCH)
# -------------------------------------------------
def get_lab_timetable(lab_room):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            day,
            slot_index,
            start_time,
            end_time,
            division,
            batch,
            subject,
            faculty
        FROM timetable
        WHERE is_lab = 1
          AND LOWER(room) = LOWER(?)
        ORDER BY division_index, day_index, slot_index
    """, (lab_room.strip(),))

    rows = cur.fetchall()
    conn.close()
    return rows


# -------------------------------------------------
# 4️⃣ CLASSROOM OCCUPIED
# -------------------------------------------------
def get_classroom_occupied(room):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            day,
            slot_index,
            start_time,
            end_time,
            division,
            subject,
            faculty
        FROM timetable
        WHERE is_lab = 0
          AND LOWER(room) = LOWER(?)
        ORDER BY division_index, day_index, slot_index
    """, (room.strip(),))

    rows = cur.fetchall()
    conn.close()
    return rows


# -------------------------------------------------
# 5️⃣ FACULTY EXPORT (GRID FORMAT)
# -------------------------------------------------
def get_faculty_timetable_for_export(faculty):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            day,
            slot_index,
            subject,
            room,
            division,
            category
        FROM timetable
        WHERE LOWER(faculty) = LOWER(?)
        ORDER BY division_index, day_index, slot_index
    """, (faculty.strip(),))

    rows = cur.fetchall()
    conn.close()
    return rows
