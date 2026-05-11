import tkinter as tk
from tkinter import ttk, messagebox, font
import sqlite3
import re
from datetime import datetime


# ─────────────────────────────────────────────
#  DATABASE LAYER
# ─────────────────────────────────────────────
class Database:
    def __init__(self, db_name="students.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                name     TEXT    NOT NULL,
                age      INTEGER NOT NULL,
                course   TEXT    NOT NULL,
                email    TEXT    UNIQUE NOT NULL,
                phone    TEXT,
                gpa      REAL,
                added_on TEXT    DEFAULT (datetime('now','localtime'))
            )
        """)
        self.conn.commit()

    def add_student(self, name, age, course, email, phone, gpa):
        try:
            self.conn.execute(
                "INSERT INTO students (name,age,course,email,phone,gpa) VALUES (?,?,?,?,?,?)",
                (name, age, course, email, phone, gpa)
            )
            self.conn.commit()
            return True, "Student added successfully."
        except sqlite3.IntegrityError:
            return False, "Email already exists."

    def get_all_students(self):
        cur = self.conn.execute(
            "SELECT id,name,age,course,email,phone,gpa,added_on FROM students ORDER BY id"
        )
        return cur.fetchall()

    def search_students(self, keyword):
        q = f"%{keyword}%"
        cur = self.conn.execute(
            "SELECT id,name,age,course,email,phone,gpa,added_on FROM students "
            "WHERE name LIKE ? OR email LIKE ? OR course LIKE ? OR CAST(id AS TEXT) LIKE ?",
            (q, q, q, q)
        )
        return cur.fetchall()

    def get_student_by_id(self, sid):
        cur = self.conn.execute(
            "SELECT id,name,age,course,email,phone,gpa FROM students WHERE id=?", (sid,)
        )
        return cur.fetchone()

    def update_student(self, sid, name, age, course, email, phone, gpa):
        try:
            self.conn.execute(
                "UPDATE students SET name=?,age=?,course=?,email=?,phone=?,gpa=? WHERE id=?",
                (name, age, course, email, phone, gpa, sid)
            )
            self.conn.commit()
            return True, "Student updated successfully."
        except sqlite3.IntegrityError:
            return False, "Email already used by another student."

    def delete_student(self, sid):
        self.conn.execute("DELETE FROM students WHERE id=?", (sid,))
        self.conn.commit()

    def count(self):
        cur = self.conn.execute("SELECT COUNT(*) FROM students")
        return cur.fetchone()[0]

    def close(self):
        self.conn.close()


# ─────────────────────────────────────────────
#  COLOUR & STYLE PALETTE
# ─────────────────────────────────────────────
C = {
    "bg":        "#0D1117",
    "panel":     "#161B22",
    "card":      "#1C2230",
    "border":    "#30363D",
    "accent":    "#58A6FF",
    "accent2":   "#3FB950",
    "warn":      "#F85149",
    "muted":     "#8B949E",
    "text":      "#E6EDF3",
    "text2":     "#C9D1D9",
    "entry_bg":  "#0D1117",
    "sel":       "#1F4073",
    "tab_act":   "#58A6FF",
    "tab_in":    "#8B949E",
    "hover_btn": "#1F6FEB",
    "danger":    "#DA3633",
    "success":   "#238636",
}

COLS = ("ID", "Name", "Age", "Course", "Email", "Phone", "GPA", "Added On")
COL_W = (50, 180, 50, 140, 200, 120, 60, 140)


# ─────────────────────────────────────────────
#  MAIN APPLICATION
# ─────────────────────────────────────────────
class StudentApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.title("Student Information System")
        self.geometry("1100x720")
        self.minsize(900, 620)
        self.configure(bg=C["bg"])
        self._apply_style()
        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ── global ttk style ──────────────────────
    def _apply_style(self):
        s = ttk.Style(self)
        s.theme_use("clam")

        # Notebook / tabs
        s.configure("Custom.TNotebook",
                     background=C["bg"], borderwidth=0, tabmargins=[0, 0, 0, 0])
        s.configure("Custom.TNotebook.Tab",
                     background=C["panel"], foreground=C["tab_in"],
                     padding=[20, 10], font=("Segoe UI", 10, "bold"),
                     borderwidth=0, relief="flat")
        s.map("Custom.TNotebook.Tab",
              background=[("selected", C["card"]), ("active", C["card"])],
              foreground=[("selected", C["tab_act"]), ("active", C["text"])],
              expand=[("selected", [0, 0, 0, 0])])

        # Treeview
        s.configure("Custom.Treeview",
                     background=C["card"], foreground=C["text2"],
                     fieldbackground=C["card"], bordercolor=C["border"],
                     rowheight=30, font=("Segoe UI", 9))
        s.configure("Custom.Treeview.Heading",
                     background=C["panel"], foreground=C["accent"],
                     font=("Segoe UI", 9, "bold"), relief="flat",
                     borderwidth=0, padding=[5, 6])
        s.map("Custom.Treeview",
              background=[("selected", C["sel"])],
              foreground=[("selected", C["text"])])

        # Scrollbar
        s.configure("Custom.Vertical.TScrollbar",
                     troughcolor=C["panel"], background=C["border"],
                     arrowcolor=C["muted"], borderwidth=0)

        # Entry / Combobox
        s.configure("Custom.TEntry",
                     fieldbackground=C["entry_bg"], foreground=C["text"],
                     insertcolor=C["text"], bordercolor=C["border"],
                     lightcolor=C["border"], darkcolor=C["border"],
                     padding=[8, 6])
        s.configure("Custom.TCombobox",
                     fieldbackground=C["entry_bg"], foreground=C["text"],
                     background=C["panel"], arrowcolor=C["accent"],
                     bordercolor=C["border"], padding=[8, 6])
        s.map("Custom.TCombobox",
              fieldbackground=[("readonly", C["entry_bg"])],
              foreground=[("readonly", C["text"])])

    # ── top header ────────────────────────────
    def _build_ui(self):
        # Header bar
        hdr = tk.Frame(self, bg=C["panel"], height=64)
        hdr.pack(fill="x", side="top")
        hdr.pack_propagate(False)

        tk.Label(hdr, text="⬡", font=("Segoe UI", 22), bg=C["panel"],
                 fg=C["accent"]).pack(side="left", padx=(20, 8), pady=12)
        tk.Label(hdr, text="Student Information System",
                 font=("Segoe UI", 16, "bold"), bg=C["panel"],
                 fg=C["text"]).pack(side="left", pady=12)

        self._stat_label = tk.Label(hdr, text="", font=("Segoe UI", 9),
                                    bg=C["panel"], fg=C["muted"])
        self._stat_label.pack(side="right", padx=24)
        self._refresh_stat()

        # Separator
        tk.Frame(self, bg=C["border"], height=1).pack(fill="x")

        # Notebook
        self.nb = ttk.Notebook(self, style="Custom.TNotebook")
        self.nb.pack(fill="both", expand=True, padx=0, pady=0)

        self._tab_add    = self._make_tab("＋  Add Student")
        self._tab_view   = self._make_tab("☰  View All")
        self._tab_search = self._make_tab("⌕  Search")
        self._tab_update = self._make_tab("✎  Update")
        self._tab_delete = self._make_tab("✕  Delete")

        self._build_add_tab(self._tab_add)
        self._build_view_tab(self._tab_view)
        self._build_search_tab(self._tab_search)
        self._build_update_tab(self._tab_update)
        self._build_delete_tab(self._tab_delete)

        # Status bar
        self._status_var = tk.StringVar(value="Ready.")
        sb = tk.Frame(self, bg=C["panel"], height=28)
        sb.pack(fill="x", side="bottom")
        tk.Frame(sb, bg=C["border"], height=1).pack(fill="x")
        tk.Label(sb, textvariable=self._status_var, font=("Segoe UI", 8),
                 bg=C["panel"], fg=C["muted"], anchor="w"
                 ).pack(fill="x", padx=12, pady=3)

    def _make_tab(self, title):
        frame = tk.Frame(self.nb, bg=C["bg"])
        self.nb.add(frame, text=title)
        return frame

    # ── shared helpers ────────────────────────
    def _set_status(self, msg, color=None):
        self._status_var.set(f"  {msg}")
        if color:
            for w in self.winfo_children():
                if isinstance(w, tk.Frame) and w.winfo_height() == 28:
                    for lbl in w.winfo_children():
                        if isinstance(lbl, tk.Label):
                            lbl.configure(fg=color)

    def _refresh_stat(self):
        n = self.db.count()
        self._stat_label.configure(
            text=f"Total Students: {n}"
        )

    def _section_label(self, parent, text):
        tk.Label(parent, text=text, font=("Segoe UI", 11, "bold"),
                 bg=C["bg"], fg=C["accent"]).pack(anchor="w", padx=32, pady=(24, 4))
        tk.Frame(parent, bg=C["border"], height=1).pack(fill="x", padx=32, pady=(0, 16))

    def _form_row(self, parent, label, row, required=False):
        """Returns (label_widget, entry_widget) packed in a grid-style frame."""
        f = tk.Frame(parent, bg=C["bg"])
        f.pack(fill="x", padx=32, pady=5)
        lbl_text = label + (" *" if required else "")
        tk.Label(f, text=lbl_text, font=("Segoe UI", 9),
                 bg=C["bg"], fg=C["muted"], width=14, anchor="e"
                 ).pack(side="left", padx=(0, 12))
        e = tk.Entry(f, font=("Segoe UI", 10), bg=C["entry_bg"],
                     fg=C["text"], insertbackground=C["text"],
                     relief="flat", bd=0,
                     highlightthickness=1,
                     highlightbackground=C["border"],
                     highlightcolor=C["accent"])
        e.pack(side="left", fill="x", expand=True, ipady=7)
        return e

    def _btn(self, parent, text, command, color=None, width=16):
        bg = color or C["accent"]
        hover = C["hover_btn"] if bg == C["accent"] else bg
        b = tk.Button(parent, text=text, command=command,
                      font=("Segoe UI", 9, "bold"), bg=bg, fg="white",
                      activebackground=hover, activeforeground="white",
                      relief="flat", bd=0, cursor="hand2",
                      width=width, padx=12, pady=8)
        b.bind("<Enter>", lambda e: b.configure(bg=hover))
        b.bind("<Leave>", lambda e: b.configure(bg=bg))
        return b

    def _tree_frame(self, parent):
        """Returns a scrollable Treeview."""
        wrap = tk.Frame(parent, bg=C["bg"])
        wrap.pack(fill="both", expand=True, padx=24, pady=(8, 16))

        tree = ttk.Treeview(wrap, columns=COLS, show="headings",
                            style="Custom.Treeview", selectmode="browse")
        for col, w in zip(COLS, COL_W):
            tree.heading(col, text=col)
            tree.column(col, width=w, minwidth=w, anchor="center")
        tree.column("Name", anchor="w")
        tree.column("Email", anchor="w")

        vsb = ttk.Scrollbar(wrap, orient="vertical", command=tree.yview,
                            style="Custom.Vertical.TScrollbar")
        tree.configure(yscrollcommand=vsb.set)
        tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        # alternating row colours
        tree.tag_configure("odd",  background=C["card"])
        tree.tag_configure("even", background=C["panel"])
        return tree

    def _populate_tree(self, tree, rows):
        tree.delete(*tree.get_children())
        for i, r in enumerate(rows):
            tag = "odd" if i % 2 == 0 else "even"
            tree.insert("", "end", values=r, tags=(tag,))

    # ── validation ────────────────────────────
    def _validate(self, name, age_s, course, email, phone_s, gpa_s):
        if not name.strip():
            return False, "Name is required."
        if not course.strip():
            return False, "Course is required."
        if not email.strip():
            return False, "Email is required."
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return False, "Invalid email address."
        try:
            age = int(age_s)
            if not (1 <= age <= 120):
                raise ValueError
        except ValueError:
            return False, "Age must be a whole number (1–120)."
        if gpa_s.strip():
            try:
                gpa = float(gpa_s)
                if not (0.0 <= gpa <= 4.0):
                    raise ValueError
            except ValueError:
                return False, "GPA must be a number between 0.0 and 4.0."
        return True, ""

    # ═══════════════════════════════════════════
    #  TAB 1 – ADD STUDENT
    # ═══════════════════════════════════════════
    def _build_add_tab(self, parent):
        self._section_label(parent, "New Student Record")

        self._add_name   = self._form_row(parent, "Full Name",  0, required=True)
        self._add_age    = self._form_row(parent, "Age",        1, required=True)
        self._add_course = self._form_row(parent, "Course",     2, required=True)
        self._add_email  = self._form_row(parent, "Email",      3, required=True)
        self._add_phone  = self._form_row(parent, "Phone",      4)
        self._add_gpa    = self._form_row(parent, "GPA (0–4.0)",5)

        note = tk.Label(parent, text="* Required fields", font=("Segoe UI", 8),
                        bg=C["bg"], fg=C["muted"])
        note.pack(anchor="w", padx=32, pady=(4, 16))

        btn_row = tk.Frame(parent, bg=C["bg"])
        btn_row.pack(anchor="w", padx=32, pady=4)
        self._btn(btn_row, "  Add Student", self._do_add).pack(side="left", padx=(0, 10))
        self._btn(btn_row, "  Clear Form", self._clear_add, color=C["border"], width=12).pack(side="left")

        self._add_msg = tk.Label(parent, text="", font=("Segoe UI", 9),
                                  bg=C["bg"], fg=C["accent2"])
        self._add_msg.pack(anchor="w", padx=32, pady=8)

    def _do_add(self):
        n  = self._add_name.get()
        a  = self._add_age.get()
        c  = self._add_course.get()
        em = self._add_email.get()
        ph = self._add_phone.get()
        gp = self._add_gpa.get()
        ok, err = self._validate(n, a, c, em, ph, gp)
        if not ok:
            self._add_msg.configure(text=f"✗  {err}", fg=C["warn"])
            return
        gpa = float(gp) if gp.strip() else None
        success, msg = self.db.add_student(n.strip(), int(a), c.strip(),
                                           em.strip(), ph.strip(), gpa)
        if success:
            self._add_msg.configure(text=f"✓  {msg}", fg=C["accent2"])
            self._clear_add()
            self._refresh_stat()
            self._set_status(msg)
        else:
            self._add_msg.configure(text=f"✗  {msg}", fg=C["warn"])

    def _clear_add(self):
        for e in (self._add_name, self._add_age, self._add_course,
                  self._add_email, self._add_phone, self._add_gpa):
            e.delete(0, "end")
        self._add_msg.configure(text="")

    # ═══════════════════════════════════════════
    #  TAB 2 – VIEW ALL
    # ═══════════════════════════════════════════
    def _build_view_tab(self, parent):
        top = tk.Frame(parent, bg=C["bg"])
        top.pack(fill="x", padx=24, pady=(20, 6))
        tk.Label(top, text="All Students", font=("Segoe UI", 11, "bold"),
                 bg=C["bg"], fg=C["accent"]).pack(side="left")
        self._btn(top, "↻  Refresh", self._do_refresh, width=10).pack(side="right")

        self._view_tree = self._tree_frame(parent)
        self._do_refresh()

    def _do_refresh(self):
        rows = self.db.get_all_students()
        self._populate_tree(self._view_tree, rows)
        self._refresh_stat()
        self._set_status(f"Loaded {len(rows)} student(s).")

    # ═══════════════════════════════════════════
    #  TAB 3 – SEARCH
    # ═══════════════════════════════════════════
    def _build_search_tab(self, parent):
        bar = tk.Frame(parent, bg=C["bg"])
        bar.pack(fill="x", padx=24, pady=(20, 8))
        tk.Label(bar, text="Search:", font=("Segoe UI", 10, "bold"),
                 bg=C["bg"], fg=C["accent"]).pack(side="left", padx=(0, 10))
        self._search_var = tk.StringVar()
        se = tk.Entry(bar, textvariable=self._search_var,
                      font=("Segoe UI", 10), bg=C["entry_bg"], fg=C["text"],
                      insertbackground=C["text"], relief="flat", bd=0,
                      highlightthickness=1, highlightbackground=C["border"],
                      highlightcolor=C["accent"], width=40)
        se.pack(side="left", ipady=7, padx=(0, 10))
        se.bind("<Return>", lambda e: self._do_search())
        self._btn(bar, "Search", self._do_search, width=10).pack(side="left")
        self._btn(bar, "Clear", self._clear_search,
                  color=C["border"], width=8).pack(side="left", padx=6)

        self._search_count = tk.Label(bar, text="", font=("Segoe UI", 8),
                                      bg=C["bg"], fg=C["muted"])
        self._search_count.pack(side="right", padx=8)

        self._search_tree = self._tree_frame(parent)

    def _do_search(self):
        kw = self._search_var.get().strip()
        if not kw:
            messagebox.showwarning("Search", "Please enter a search term.", parent=self)
            return
        rows = self.db.search_students(kw)
        self._populate_tree(self._search_tree, rows)
        self._search_count.configure(text=f"{len(rows)} result(s)")
        self._set_status(f"Search '{kw}' → {len(rows)} result(s).")

    def _clear_search(self):
        self._search_var.set("")
        self._search_tree.delete(*self._search_tree.get_children())
        self._search_count.configure(text="")

    # ═══════════════════════════════════════════
    #  TAB 4 – UPDATE
    # ═══════════════════════════════════════════
    def _build_update_tab(self, parent):
        self._section_label(parent, "Update Student Record")

        id_row = tk.Frame(parent, bg=C["bg"])
        id_row.pack(fill="x", padx=32, pady=(0, 12))
        tk.Label(id_row, text="Student ID *", font=("Segoe UI", 9),
                 bg=C["bg"], fg=C["muted"], width=14, anchor="e"
                 ).pack(side="left", padx=(0, 12))
        self._upd_id = tk.Entry(id_row, font=("Segoe UI", 10),
                                bg=C["entry_bg"], fg=C["text"],
                                insertbackground=C["text"], relief="flat",
                                bd=0, highlightthickness=1,
                                highlightbackground=C["border"],
                                highlightcolor=C["accent"], width=12)
        self._upd_id.pack(side="left", ipady=7, padx=(0, 10))
        self._btn(id_row, "Load", self._do_load_student, width=8).pack(side="left")

        self._upd_name   = self._form_row(parent, "Full Name",   0, required=True)
        self._upd_age    = self._form_row(parent, "Age",         1, required=True)
        self._upd_course = self._form_row(parent, "Course",      2, required=True)
        self._upd_email  = self._form_row(parent, "Email",       3, required=True)
        self._upd_phone  = self._form_row(parent, "Phone",       4)
        self._upd_gpa    = self._form_row(parent, "GPA (0–4.0)", 5)

        btn_row = tk.Frame(parent, bg=C["bg"])
        btn_row.pack(anchor="w", padx=32, pady=(12, 4))
        self._btn(btn_row, "  Save Changes",
                  self._do_update, color=C["success"]).pack(side="left", padx=(0, 10))
        self._btn(btn_row, "  Clear",
                  self._clear_update, color=C["border"], width=10).pack(side="left")

        self._upd_msg = tk.Label(parent, text="", font=("Segoe UI", 9),
                                  bg=C["bg"], fg=C["accent2"])
        self._upd_msg.pack(anchor="w", padx=32, pady=6)

    def _do_load_student(self):
        sid = self._upd_id.get().strip()
        if not sid.isdigit():
            self._upd_msg.configure(text="✗  Enter a valid numeric ID.", fg=C["warn"])
            return
        rec = self.db.get_student_by_id(int(sid))
        if not rec:
            self._upd_msg.configure(text=f"✗  No student with ID {sid}.", fg=C["warn"])
            return
        _, name, age, course, email, phone, gpa = rec
        for entry, val in zip(
            (self._upd_name, self._upd_age, self._upd_course,
             self._upd_email, self._upd_phone, self._upd_gpa),
            (name, age, course, email, phone or "", gpa if gpa is not None else "")
        ):
            entry.delete(0, "end")
            entry.insert(0, str(val))
        self._upd_msg.configure(text=f"✓  Loaded student ID {sid}.", fg=C["accent"])

    def _do_update(self):
        sid = self._upd_id.get().strip()
        if not sid.isdigit():
            self._upd_msg.configure(text="✗  Load a student first.", fg=C["warn"])
            return
        n  = self._upd_name.get()
        a  = self._upd_age.get()
        c  = self._upd_course.get()
        em = self._upd_email.get()
        ph = self._upd_phone.get()
        gp = self._upd_gpa.get()
        ok, err = self._validate(n, a, c, em, ph, gp)
        if not ok:
            self._upd_msg.configure(text=f"✗  {err}", fg=C["warn"])
            return
        gpa = float(gp) if gp.strip() else None
        success, msg = self.db.update_student(int(sid), n.strip(), int(a),
                                               c.strip(), em.strip(),
                                               ph.strip(), gpa)
        color = C["accent2"] if success else C["warn"]
        icon  = "✓" if success else "✗"
        self._upd_msg.configure(text=f"{icon}  {msg}", fg=color)
        if success:
            self._refresh_stat()
            self._set_status(msg)

    def _clear_update(self):
        self._upd_id.delete(0, "end")
        for e in (self._upd_name, self._upd_age, self._upd_course,
                  self._upd_email, self._upd_phone, self._upd_gpa):
            e.delete(0, "end")
        self._upd_msg.configure(text="")

    # ═══════════════════════════════════════════
    #  TAB 5 – DELETE
    # ═══════════════════════════════════════════
    def _build_delete_tab(self, parent):
        self._section_label(parent, "Delete Student Record")

        tk.Label(parent,
                 text="Enter the Student ID to permanently remove the record.",
                 font=("Segoe UI", 9), bg=C["bg"], fg=C["muted"]
                 ).pack(anchor="w", padx=32, pady=(0, 20))

        id_row = tk.Frame(parent, bg=C["bg"])
        id_row.pack(fill="x", padx=32, pady=4)
        tk.Label(id_row, text="Student ID *", font=("Segoe UI", 9),
                 bg=C["bg"], fg=C["muted"], width=14, anchor="e"
                 ).pack(side="left", padx=(0, 12))
        self._del_id = tk.Entry(id_row, font=("Segoe UI", 10),
                                bg=C["entry_bg"], fg=C["text"],
                                insertbackground=C["text"], relief="flat",
                                bd=0, highlightthickness=1,
                                highlightbackground=C["border"],
                                highlightcolor=C["accent"], width=14)
        self._del_id.pack(side="left", ipady=7, padx=(0, 10))
        self._btn(id_row, "Lookup", self._do_lookup_delete, width=9).pack(side="left")

        # Preview card
        self._del_preview = tk.Frame(parent, bg=C["card"],
                                     highlightthickness=1,
                                     highlightbackground=C["border"])
        self._del_preview.pack(fill="x", padx=32, pady=16)
        self._del_preview_lbl = tk.Label(self._del_preview,
                                          text="No student loaded.",
                                          font=("Segoe UI", 9),
                                          bg=C["card"], fg=C["muted"],
                                          justify="left", padx=16, pady=12)
        self._del_preview_lbl.pack(anchor="w")

        btn_row = tk.Frame(parent, bg=C["bg"])
        btn_row.pack(anchor="w", padx=32, pady=4)
        self._del_btn = self._btn(btn_row, "  Delete Student",
                                   self._do_delete, color=C["danger"])
        self._del_btn.pack(side="left", padx=(0, 10))
        self._btn(btn_row, "  Clear",
                  self._clear_delete, color=C["border"], width=10).pack(side="left")

        self._del_msg = tk.Label(parent, text="", font=("Segoe UI", 9),
                                  bg=C["bg"], fg=C["accent2"])
        self._del_msg.pack(anchor="w", padx=32, pady=6)
        self._del_target = None

    def _do_lookup_delete(self):
        sid = self._del_id.get().strip()
        if not sid.isdigit():
            self._del_msg.configure(text="✗  Enter a valid numeric ID.", fg=C["warn"])
            return
        rec = self.db.get_student_by_id(int(sid))
        if not rec:
            self._del_msg.configure(text=f"✗  No student with ID {sid}.", fg=C["warn"])
            self._del_preview_lbl.configure(text="No student found.", fg=C["muted"])
            self._del_target = None
            return
        sid_r, name, age, course, email, phone, gpa = rec
        self._del_target = sid_r
        info = (f"  ID: {sid_r}    Name: {name}    Age: {age}\n"
                f"  Course: {course}    Email: {email}\n"
                f"  Phone: {phone or '—'}    GPA: {gpa if gpa is not None else '—'}")
        self._del_preview_lbl.configure(text=info, fg=C["text2"])
        self._del_msg.configure(text="")

    def _do_delete(self):
        if self._del_target is None:
            self._del_msg.configure(text="✗  Lookup a student first.", fg=C["warn"])
            return
        sid = self._del_target
        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to permanently delete student ID {sid}?\n"
            "This action cannot be undone.",
            parent=self, icon="warning"
        )
        if confirm:
            self.db.delete_student(sid)
            self._del_msg.configure(
                text=f"✓  Student ID {sid} has been deleted.", fg=C["accent2"])
            self._del_preview_lbl.configure(text="No student loaded.", fg=C["muted"])
            self._del_target = None
            self._del_id.delete(0, "end")
            self._refresh_stat()
            self._set_status(f"Student ID {sid} deleted.")

    def _clear_delete(self):
        self._del_id.delete(0, "end")
        self._del_preview_lbl.configure(text="No student loaded.", fg=C["muted"])
        self._del_msg.configure(text="")
        self._del_target = None

    # ── close ─────────────────────────────────
    def _on_close(self):
        self.db.close()
        self.destroy()


# ─────────────────────────────────────────────
if __name__ == "__main__":
    app = StudentApp()
    app.mainloop()