'''
A simple Tkinter GUI client that interacts with the FastAPI API. It provides basic
functionality to create/list Students, Courses, and Teachers, and to enroll/unenroll students.
Run this as a separate process after starting the FastAPI server (python main.py).
'''
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import requests
API_BASE = "http://127.0.0.1:8000/api"
class SchoolClientGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("School Client GUI")
        self.geometry("900x600")
        tab_control = ttk.Notebook(self)
        self.student_tab = ttk.Frame(tab_control)
        self.course_tab = ttk.Frame(tab_control)
        self.teacher_tab = ttk.Frame(tab_control)
        self.enroll_tab = ttk.Frame(tab_control)
        tab_control.add(self.student_tab, text="Students")
        tab_control.add(self.course_tab, text="Courses")
        tab_control.add(self.teacher_tab, text="Teachers")
        tab_control.add(self.enroll_tab, text="Enrollments")
        tab_control.pack(expand=1, fill="both")
        # Build each tab
        self.build_student_tab()
        self.build_course_tab()
        self.build_teacher_tab()
        self.build_enroll_tab()
    # ---------------- Students Tab ----------------
    def build_student_tab(self):
        frame = self.student_tab
        # Form
        form = ttk.LabelFrame(frame, text="Create Student")
        form.pack(side="top", fill="x", padx=8, pady=8)
        ttk.Label(form, text="Name:").grid(row=0, column=0, sticky="w")
        self.s_name = ttk.Entry(form, width=40)
        self.s_name.grid(row=0, column=1, padx=4, pady=2)
        ttk.Label(form, text="Email:").grid(row=1, column=0, sticky="w")
        self.s_email = ttk.Entry(form, width=40)
        self.s_email.grid(row=1, column=1, padx=4, pady=2)
        ttk.Button(form, text="Create", command=self.create_student).grid(row=2, column=1, sticky="e", pady=4)
        # List
        list_frame = ttk.LabelFrame(frame, text="Students List")
        list_frame.pack(side="top", fill="both", expand=True, padx=8, pady=8)
        self.student_listbox = tk.Listbox(list_frame)
        self.student_listbox.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.student_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.student_listbox.config(yscrollcommand=scrollbar.set)
        ttk.Button(frame, text="Refresh Students", command=self.load_students).pack(pady=4)
        self.load_students()
    def create_student(self):
        name = self.s_name.get().strip()
        email = self.s_email.get().strip()
        if not name or not email:
            messagebox.showerror("Error", "Name and Email are required")
            return
        payload = {"name": name, "email": email}
        try:
            r = requests.post(f"{API_BASE}/students/", json=payload)
            r.raise_for_status()
            messagebox.showinfo("Success", "Student created")
            self.s_name.delete(0, tk.END)
            self.s_email.delete(0, tk.END)
            self.load_students()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create student: {e}\n{getattr(r, 'text', '')}")
    def load_students(self):
        try:
            r = requests.get(f"{API_BASE}/students/")
            r.raise_for_status()
            students = r.json()
            self.student_listbox.delete(0, tk.END)
            for s in students:
                courses = ", ".join([c["title"] for c in s.get("courses", [])])
                self.student_listbox.insert(tk.END, f"{s['id']}: {s['name']} <{s['email']}> - Courses: [{courses}]")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load students: {e}")
    # ---------------- Courses Tab ----------------
    def build_course_tab(self):
        frame = self.course_tab
        form = ttk.LabelFrame(frame, text="Create Course")
        form.pack(side="top", fill="x", padx=8, pady=8)
        ttk.Label(form, text="Title:").grid(row=0, column=0, sticky="w")
        self.c_title = ttk.Entry(form, width=40)
        self.c_title.grid(row=0, column=1, padx=4, pady=2)
        ttk.Label(form, text="Level (int):").grid(row=1, column=0, sticky="w")
        self.c_level = ttk.Entry(form, width=10)
        self.c_level.grid(row=1, column=1, padx=4, pady=2, sticky="w")
        ttk.Label(form, text="Teacher ID (optional):").grid(row=2, column=0, sticky="w")
        self.c_teacher_id = ttk.Entry(form, width=10)
        self.c_teacher_id.grid(row=2, column=1, padx=4, pady=2, sticky="w")
        ttk.Button(form, text="Create", command=self.create_course).grid(row=3, column=1, sticky="e", pady=4)
        list_frame = ttk.LabelFrame(frame, text="Courses List")
        list_frame.pack(side="top", fill="both", expand=True, padx=8, pady=8)
        self.course_listbox = tk.Listbox(list_frame)
        self.course_listbox.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.course_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.course_listbox.config(yscrollcommand=scrollbar.set)
        ttk.Button(frame, text="Refresh Courses", command=self.load_courses).pack(pady=4)
        self.load_courses()
    def create_course(self):
        title = self.c_title.get().strip()
        level_text = self.c_level.get().strip()
        teacher_text = self.c_teacher_id.get().strip()
        if not title or not level_text:
            messagebox.showerror("Error", "Title and Level are required")
            return
        try:
            level = int(level_text)
        except ValueError:
            messagebox.showerror("Error", "Level must be an integer")
            return
        payload = {"title": title, "level": level}
        if teacher_text:
            try:
                teacher_id = int(teacher_text)
                payload["teacher_id"] = teacher_id
            except ValueError:
                messagebox.showerror("Error", "Teacher ID must be an integer")
                return
        try:
            r = requests.post(f"{API_BASE}/courses/", json=payload)
            r.raise_for_status()
            messagebox.showinfo("Success", "Course created")
            self.c_title.delete(0, tk.END)
            self.c_level.delete(0, tk.END)
            self.c_teacher_id.delete(0, tk.END)
            self.load_courses()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create course: {e}\n{getattr(r, 'text', '')}")
    def load_courses(self):
        try:
            r = requests.get(f"{API_BASE}/courses/")
            r.raise_for_status()
            courses = r.json()
            self.course_listbox.delete(0, tk.END)
            for c in courses:
                teacher = c.get("teacher")
                teacher_str = f"{teacher['name']} (id={teacher['id']})" if teacher else "None"
                students = ", ".join([s["name"] for s in c.get("students", [])])
                self.course_listbox.insert(
                    tk.END,
                    f"{c['id']}: {c['title']} (Level {c['level']}) - Teacher: {teacher_str} - Students: [{students}]",
                )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load courses: {e}")
    # ---------------- Teachers Tab ----------------
    def build_teacher_tab(self):
        frame = self.teacher_tab
        form = ttk.LabelFrame(frame, text="Create Teacher")
        form.pack(side="top", fill="x", padx=8, pady=8)
        ttk.Label(form, text="Name:").grid(row=0, column=0, sticky="w")
        self.t_name = ttk.Entry(form, width=40)
        self.t_name.grid(row=0, column=1, padx=4, pady=2)
        ttk.Button(form, text="Create", command=self.create_teacher).grid(row=1, column=1, sticky="e", pady=4)
        list_frame = ttk.LabelFrame(frame, text="Teachers List")
        list_frame.pack(side="top", fill="both", expand=True, padx=8, pady=8)
        self.teacher_listbox = tk.Listbox(list_frame)
        self.teacher_listbox.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.teacher_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.teacher_listbox.config(yscrollcommand=scrollbar.set)
        ttk.Button(frame, text="Refresh Teachers", command=self.load_teachers).pack(pady=4)
        self.load_teachers()
    def create_teacher(self):
        name = self.t_name.get().strip()
        if not name:
            messagebox.showerror("Error", "Name is required")
            return
        payload = {"name": name}
        try:
            r = requests.post(f"{API_BASE}/teachers/", json=payload)
            r.raise_for_status()
            messagebox.showinfo("Success", "Teacher created")
            self.t_name.delete(0, tk.END)
            self.load_teachers()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create teacher: {e}\n{getattr(r, 'text', '')}")
    def load_teachers(self):
        try:
            r = requests.get(f"{API_BASE}/teachers/")
            r.raise_for_status()
            teachers = r.json()
            self.teacher_listbox.delete(0, tk.END)
            for t in teachers:
                self.teacher_listbox.insert(tk.END, f"{t['id']}: {t['name']}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load teachers: {e}")
    # ---------------- Enroll Tab ----------------
    def build_enroll_tab(self):
        frame = self.enroll_tab
        form = ttk.LabelFrame(frame, text="Enroll / Unenroll Student")
        form.pack(side="top", fill="x", padx=8, pady=8)
        ttk.Label(form, text="Student ID:").grid(row=0, column=0, sticky="w")
        self.e_student_id = ttk.Entry(form, width=10)
        self.e_student_id.grid(row=0, column=1, padx=4, pady=2)
        ttk.Label(form, text="Course ID:").grid(row=1, column=0, sticky="w")
        self.e_course_id = ttk.Entry(form, width=10)
        self.e_course_id.grid(row=1, column=1, padx=4, pady=2)
        btn_frame = ttk.Frame(form)
        btn_frame.grid(row=2, column=0, columnspan=2, sticky="e", pady=4)
        ttk.Button(btn_frame, text="Enroll", command=self.enroll).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Unenroll", command=self.unenroll).pack(side="left", padx=4)
        ttk.Label(frame, text="Tip: Use the Students and Courses tabs to discover IDs.").pack(pady=8)
    def enroll(self):
        s_id = self.e_student_id.get().strip()
        c_id = self.e_course_id.get().strip()
        if not s_id or not c_id:
            messagebox.showerror("Error", "Student ID and Course ID are required")
            return
        try:
            r = requests.post(f"{API_BASE}/students/{int(s_id)}/enroll/{int(c_id)}")
            r.raise_for_status()
            messagebox.showinfo("Success", "Enrolled student")
            self.load_students()
            self.load_courses()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to enroll student: {e}\n{getattr(r, 'text', '')}")
    def unenroll(self):
        s_id = self.e_student_id.get().strip()
        c_id = self.e_course_id.get().strip()
        if not s_id or not c_id:
            messagebox.showerror("Error", "Student ID and Course ID are required")
            return
        try:
            r = requests.delete(f"{API_BASE}/students/{int(s_id)}/unenroll/{int(c_id)}")
            r.raise_for_status()
            messagebox.showinfo("Success", "Unenrolled student")
            self.load_students()
            self.load_courses()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to unenroll student: {e}\n{getattr(r, 'text', '')}")
def run_gui():
    app = SchoolClientGUI()
    app.mainloop()
if __name__ == "__main__":
    # Run the GUI in the main thread
    run_gui()