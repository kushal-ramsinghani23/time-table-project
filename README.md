---

# Automated Timetable Management System

## 📌 Project Overview

The **Automated Timetable Management System** is a desktop-based software application designed to automatically extract, store, and present academic timetable information from a **centralized department timetable** (PDF format).

The system eliminates manual timetable handling and provides **accurate, fast, and reliable retrieval** of

* Individual **Faculty Timetable**
* Individual **Division / Class Timetable**
* **Laboratory Occupancy**
* **Classroom Occupancy**

The application is built using **Python**, with **Tkinter** for the GUI, **SQLite** for storage, and supports exporting timetables to **Microsoft Word** format.

---

## 🎯 Objectives

* Reduce manual effort in timetable handling
* Avoid conflicts and inconsistencies
* Provide a centralized, query-based timetable system
* Support full-semester timetable visualization
* Enable professional document export for academic use

---

## 🧩 Key Features

### 1️⃣ Faculty Timetable

* Displays the **complete semester workload** of a faculty
* Handles:

  * Multiple divisions
  * Labs occupying two time slots
  * Electives
* Merges multiple lectures in the same slot intelligently

### 2️⃣ Division / Class Timetable

* Shows the **day-wise, slot-wise timetable** of a selected division
* Includes subject, faculty, and classroom/lab details

### 3️⃣ Lab Occupancy

* Displays **batch-wise lab usage**
* Ensures no overlap or conflict
* Correctly handles labs spanning multiple slots

### 4️⃣ Classroom Occupancy

* Shows classroom usage across divisions
* Uses default classrooms per division where applicable

### 5️⃣ Export to Word

* Timetables can be exported as **`.docx`**
* Output matches the **UI grid structure**
* Suitable for printing and official documentation

---

## 🛠️ Technology Stack

| Component            | Technology   |
| -------------------- | ------------ |
| Programming Language | Python 3     |
| GUI                  | Tkinter      |
| Database             | SQLite       |
| PDF Parsing          | pdfplumber   |
| Data Processing      | pandas       |
| Document Export      | python-docx  |
| Version Control      | Git & GitHub |

---

## 🗂️ Project Structure

```
time-table-project/
│
├── src/
│   ├── ui/                # Tkinter UI
│   │   └── ui.py
│   │
│   ├── importers/         # PDF / Excel import logic
│   │   ├── pdf_to_db.py
|   |   ├── pdf_to_excel.py
│   │   └── excel_to_db.py
│   │
│   ├── services/          # DB query services
│   │   └── services.py
│   │
│   ├── exporters/         # Word export
│   │   └── export_word.py
│   │
│   ├── db/                # Database connection
│   │   └── database.py
│   │
│   └── utils/             # Normalization & helpers
│
├── README.md
└── .gitignore
```

> ⚠️ Only the `src/` directory is tracked in Git.
> Generated data (PDFs, DB, Excel, Word files) are intentionally ignored.

---

## 🔄 System Workflow

1. **PDF Input**

   * Centralized department timetable (PDF)

2. **PDF Parsing**

   * Extracts:

     * Day
     * Time slot
     * Division
     * Batch
     * Subject
     * Faculty
     * Room / Lab
   * Handles edge cases:

     * `/` and `\` separators
     * Multiple entries in one cell
     * Labs occupying two slots

3. **Database Storage**

   * Normalized SQLite schema
   * Indexed for fast retrieval
   * Day and division ordering preserved

4. **User Interaction (UI)**

   * Select timetable type
   * View grid-based timetable
  
5. **Export**

   * Generate Word documents matching UI format

---

## 🎨 UI Enhancements

* Grid-based timetable layout
* Row striping for readability
* Intelligent merging of overlapping lectures
* Responsive resizing

---

## 🧠 Design Decisions

* **SQLite** chosen for simplicity and portability
* **Layered architecture** (UI → Services → DB)
* **Slot-based model** to handle labs spanning multiple periods
* **Normalization before DB insert** to ensure consistency
* **No hardcoding in UI** – all data is DB-driven

---

## ⚠️ Assumptions & Constraints

* Input PDF follows a tabular timetable structure
* Days are Monday–Friday
* Time slots are fixed per semester
* One division has one default classroom
* Labs always occupy two consecutive slots

---

## 🚀 Future Enhancements

* Faculty conflict detection
* PDF export
* Dark mode UI
* Web-based version
* Admin dashboard for timetable updates

---

## 👨‍🎓 Academic Relevance

This project demonstrates:

* Real-world data extraction
* Database normalization
* GUI-based information systems
* Robust edge-case handling
* Software engineering best practices

It is suitable for:

* Mini project
* Final year project
* Viva and practical examinations

---

## 📜 License

This project is developed for **academic purposes**.

---

