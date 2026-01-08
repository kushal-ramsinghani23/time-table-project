import tkinter as tk
from tkinter import ttk, messagebox
from collections import defaultdict

from src.services.services import (
    get_faculty_timetable,
    get_division_timetable,
    get_lab_timetable,
    get_classroom_occupied
)

from src.exporters.export_word import (
    export_faculty_timetable,
    export_division_timetable,
    export_lab_occupied,
    export_classroom_occupied
)

# -------------------------------------------------
# CONSTANTS
# -------------------------------------------------
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

TIME_SLOTS = [
    "08:30 - 09:30",
    "09:30 - 10:30",
    "10:30 - 11:30",
    "11:30 - 12:30",
    "12:30 - 13:30",
    "13:30 - 14:30",
    "14:30 - 15:30",
    "15:30 - 16:30",
    "16:30 - 17:30",
    "17:30 - 18:30",
]

# -------------------------------------------------
# MAIN WINDOW
# -------------------------------------------------
root = tk.Tk()
root.title("Automated Timetable Management System")
root.geometry("1200x720")
root.minsize(1000, 600)

root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1)

# -------------------------------------------------
# STYLE (GRID + BORDERS)
# -------------------------------------------------
style = ttk.Style()
style.theme_use("default")

style.configure(
    "Treeview",
    background="white",
    foreground="black",
    rowheight=80,
    fieldbackground="white",
    bordercolor="#333",
    borderwidth=1,
    relief="solid",
    font=("Arial", 9)
)

style.configure(
    "Treeview.Heading",
    background="#e0e0e0",
    foreground="black",
    relief="solid",
    borderwidth=1,
    font=("Arial", 10, "bold")
)

style.map(
    "Treeview",
    background=[("selected", "#cce5ff")]
)

# -------------------------------------------------
# TOP FRAME
# -------------------------------------------------
top_frame = tk.Frame(root)
top_frame.grid(row=0, column=0, pady=10, sticky="w")

tk.Label(
    top_frame,
    text="Select Timetable Type",
    font=("Arial", 10, "bold")
).grid(row=0, column=0, padx=5, sticky="w")

mode = ttk.Combobox(
    top_frame,
    values=[
        "Faculty Timetable",
        "Division Timetable",
        "Lab Occupied",
        "Classroom Occupied"
    ],
    state="readonly",
    width=30
)
mode.grid(row=0, column=1, padx=5)
mode.current(0)

tk.Label(
    top_frame,
    text="Enter Faculty / Division / Lab / Room"
).grid(row=1, column=0, pady=5, sticky="w")

input_entry = tk.Entry(top_frame, width=32)
input_entry.grid(row=1, column=1, padx=5)

# -------------------------------------------------
# TABLE FRAME (RESPONSIVE)
# -------------------------------------------------
table_frame = tk.Frame(root, bd=2, relief="solid")
table_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)

table_frame.grid_rowconfigure(0, weight=1)
table_frame.grid_columnconfigure(0, weight=1)

columns = ["Time"] + DAYS
table = ttk.Treeview(
    table_frame,
    columns=columns,
    show="headings"
)

# Time column fixed, others stretch
table.heading("Time", text="Time")
table.column("Time", width=140, anchor="center", stretch=False)

for day in DAYS:
    table.heading(day, text=day)
    table.column(day, anchor="center", stretch=True)

# Scrollbar
scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=table.yview)
table.configure(yscrollcommand=scrollbar.set)

table.grid(row=0, column=0, sticky="nsew")
scrollbar.grid(row=0, column=1, sticky="ns")

# -------------------------------------------------
# ROW STRIPES
# -------------------------------------------------
table.tag_configure("even", background="#ffffff")
table.tag_configure("odd", background="#f4f6f8")
table.tag_configure("timecol", font=("Arial", 9, "bold"))

# -------------------------------------------------
# BUILD EMPTY GRID
# -------------------------------------------------
def build_empty_grid():
    table.delete(*table.get_children())
    for i, slot in enumerate(TIME_SLOTS):
        tag = "even" if i % 2 == 0 else "odd"
        table.insert(
            "",
            tk.END,
            values=[slot] + [""] * 5,
            tags=(tag, "timecol")
        )

# -------------------------------------------------
# LOAD DATA (CORRECT FORMAT)
# -------------------------------------------------
def load_data():
    selected_mode = mode.get()
    value = input_entry.get().strip()

    if not selected_mode or not value:
        messagebox.showwarning("Input Required", "Select mode and enter value")
        return

    build_empty_grid()
    grid = defaultdict(list)

    if selected_mode == "Faculty Timetable":
        records = get_faculty_timetable(value)
        for d, slot, _, _, div, batch, sub, room, is_lab, category in records:
            line = f"{sub} / {div} / {room}"
            if category == "C":
                line += " (Elective)"
            grid[(d, slot)].append(line)

    elif selected_mode == "Division Timetable":
        records = get_division_timetable(value)
        for d, slot, _, _, sub, fac, room, category in records:
            line = f"{sub} / {fac} / {room}"
            if category == "C":
                line += " (Elective)"
            grid[(d, slot)].append(line)

    elif selected_mode == "Lab Occupied":
        records = get_lab_timetable(value)
        for d, slot, _, _, div, batch, sub, fac in records:
            grid[(d, slot)].append(f"{sub} / {div} / {fac}")

    elif selected_mode == "Classroom Occupied":
        records = get_classroom_occupied(value)
        for d, slot, _, _, div, sub, fac in records:
            grid[(d, slot)].append(f"{sub} / {div} / {fac}")

    for row_id in table.get_children():
        row = table.item(row_id)["values"]
        slot_index = table.index(row_id) + 1

        for i, day in enumerate(DAYS):
            if (day, slot_index) in grid:
                row[i + 1] = "\n".join(grid[(day, slot_index)])

        table.item(row_id, values=row)

# -------------------------------------------------
# EXPORT WORD
# -------------------------------------------------
def export_word():
    value = input_entry.get().strip()
    selected_mode = mode.get()

    if not value:
        messagebox.showwarning("Input Required", "Enter value first")
        return

    if selected_mode == "Faculty Timetable":
        path = export_faculty_timetable(value)
    elif selected_mode == "Division Timetable":
        path = export_division_timetable(value)
    elif selected_mode == "Lab Occupied":
        path = export_lab_occupied(value)
    elif selected_mode == "Classroom Occupied":
        path = export_classroom_occupied(value)
    else:
        return

    messagebox.showinfo("Export Successful", f"Saved at:\n{path}")

# -------------------------------------------------
# BUTTONS
# -------------------------------------------------
button_frame = tk.Frame(root)
button_frame.grid(row=2, column=0, pady=15)

tk.Button(
    button_frame,
    text="View Timetable",
    command=load_data,
    width=30,
    bg="#1976d2",
    fg="white",
    font=("Arial", 10, "bold")
).grid(row=0, column=0, padx=15)

tk.Button(
    button_frame,
    text="Export Timetable (Word)",
    command=export_word,
    width=35,
    bg="#2e7d32",
    fg="white",
    font=("Arial", 10, "bold")
).grid(row=0, column=1, padx=15)

# -------------------------------------------------
# INIT
# -------------------------------------------------
build_empty_grid()
root.mainloop()
