from src.db.database import get_connection

conn = get_connection()
cur = conn.cursor()

cur.execute("SELECT COUNT(*) FROM timetable")
print("Row count:", cur.fetchone()[0])

conn.close()
