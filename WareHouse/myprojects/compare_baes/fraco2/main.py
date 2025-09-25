'''
Simple Tkinter GUI client for interacting with the FastAPI server.
Requires the FastAPI server to be running (default at http://127.0.0.1:8000).
Provides tabs for Students, Courses, and Teachers with basic CRUD operations and relationship handling.
'''
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import requests
API_URL = "http://127.0.0.1:8000"
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("School Management GUI Client")
        self.geometry("900x600")
        tab_control = ttk.Notebook(self)
        self.student_tab = StudentTab(tab_control)
        self.course_tab = CourseTab(tab_control)
        self.teacher_tab = TeacherTab(tab_control)
        tab_control.add(self.student_tab, text="Students")
        tab_control.add(self.course_tab, text="Courses")
        tab_control.add(self.teacher_tab, text="Teachers")
        tab_control.pack(expand=1, fill="both")
class StudentTab(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        # Left frame: forms
        left = ttk.Frame(self)
        left.pack(side="left", fill="y", padx=10, pady=10)
        ttk.Label(left, text="Name:").pack(anchor="w")
        self.name_entry = ttk.Entry(left, width=30)
        self.name_entry.pack(anchor="w")
        ttk.Label(left, text="Email:").pack(anchor="w")
        self.email_entry = ttk.Entry(left, width=30)
        self.email_entry.pack(anchor="w")
        ttk.Button(left, text="Create Student", command=self.create_student).pack(pady=5)
        ttk.Button(left, text="Refresh List", command=self.refresh_students).pack(pady=5)
        ttk.Separator(left, orient="horizontal").pack(fill="x", pady=10)
        ttk.Label(left, text="Enroll/Unenroll").pack(anchor="w")
        ttk.Button(left, text="Enroll Selected in Course", command=self.enroll_selected_in_course).pack(pady=3)
        ttk.Button(left, text="Unenroll Selected from Course", command=self.unenroll_selected_from_course).pack(pady=3)
        ttk.Button(left, text="Show Student Courses", command=self.show_student_courses).pack(pady=3)
        # Right frame: list
        right = ttk.Frame(self)
        right.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        columns = ("id", "name", "email")
        self.tree = ttk.Treeview(right, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col.title())
            self.tree.column(col, width=150)
        self.tree.pack(fill="both", expand=True)
        self.refresh_students()
        # For selecting course when enrolling
        self.course_select_window = None
    def create_student(self):
        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()
        if not name or not email:
            messagebox.showwarning("Validation", "Name and Email are required")
            return
        try:
            r = requests.post(f"{API_URL}/students/", json={"name": name, "email": email})
            if r.status_code == 201:
                messagebox.showinfo("Success", "Student created")
                self.name_entry.delete(0, tk.END)
                self.email_entry.delete(0, tk.END)
                self.refresh_students()
            else:
                messagebox.showerror("Error", f"Failed to create student: {r.text}")
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Connection Error", "Failed to reach API. Is the server running?")
    def refresh_students(self):
        try:
            r = requests.get(f"{API_URL}/students/")
            if r.status_code == 200:
                for i in self.tree.get_children():
                    self.tree.delete(i)
                for s in r.json():
                    self.tree.insert("", tk.END, values=(s["id"], s["name"], s["email"]))
            else:
                messagebox.showerror("Error", f"Failed to list students: {r.text}")
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Connection Error", "Failed to reach API. Is the server running?")
    def get_selected_student_id(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Selection", "No student selected")
            return None
        item = self.tree.item(sel[0])
        return item["values"][0]
    def enroll_selected_in_course(self):
        sid = self.get_selected_student_id()
        if not sid:
            return
        CourseSelector(self, action="enroll", student_id=sid)
    def unenroll_selected_from_course(self):
        sid = self.get_selected_student_id()
        if not sid:
            return
        # show list of courses student is enrolled in
        try:
            r = requests.get(f"{API_URL}/students/{sid}/courses")
            if r.status_code != 200:
                messagebox.showerror("Error", f"Failed to fetch courses: {r.text}")
                return
            courses = r.json()
            if not courses:
                messagebox.showinfo("Info", "Student is not enrolled in any courses")
                return
            CourseSelector(self, action="unenroll", student_id=sid, courses=courses)
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Connection Error", "Failed to reach API. Is the server running?")
    def show_student_courses(self):
        sid = self.get_selected_student_id()
        if not sid:
            return
        try:
            r = requests.get(f"{API_URL}/students/{sid}/courses")
            if r.status_code == 200:
                courses = r.json()
                if not courses:
                    messagebox.showinfo("Courses", "No courses enrolled")
                    return
                text = "\n".join([f"{c['id']}: {c['title']} (Level: {c.get('level')})" for c in courses])
                messagebox.showinfo("Student Courses", text)
            else:
                messagebox.showerror("Error", f"Failed to fetch student courses: {r.text}")
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Connection Error", "Failed to reach API. Is the server running?")
class CourseSelector(tk.Toplevel):
    def __init__(self, parent, action: str, student_id: int, courses=None):
        super().__init__(parent)
        self.action = action  # enroll or unenroll
        self.student_id = student_id
        self.title("Select Course")
        self.geometry("400x300")
        self.parent = parent
        ttk.Label(self, text="Available Courses:").pack(anchor="w", padx=10, pady=5)
        self.listbox = tk.Listbox(self)
        self.listbox.pack(fill="both", expand=True, padx=10, pady=5)
        if self.action == "enroll":
            # fetch all courses
            try:
                r = requests.get(f"{API_URL}/courses/")
                if r.status_code == 200:
                    self.courses = r.json()
                else:
                    self.courses = []
            except requests.exceptions.ConnectionError:
                self.courses = []
            for c in self.courses:
                self.listbox.insert(tk.END, f"{c['id']}: {c['title']} (Level: {c.get('level')})")
            ttk.Button(self, text="Enroll", command=self.perform).pack(pady=5)
        else:
            # courses is provided (student's courses)
            self.courses = courses or []
            for c in self.courses:
                self.listbox.insert(tk.END, f"{c['id']}: {c['title']} (Level: {c.get('level')})")
            ttk.Button(self, text="Unenroll", command=self.perform).pack(pady=5)
    def perform(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning("Selection", "No course selected")
            return
        chosen = self.courses[sel[0]]
        course_id = chosen["id"]
        try:
            if self.action == "enroll":
                r = requests.post(f"{API_URL}/students/{self.student_id}/enroll/{course_id}")
                if r.status_code == 200:
                    messagebox.showinfo("Success", "Student enrolled")
                    self.parent.refresh_students()
                    self.destroy()
                else:
                    messagebox.showerror("Error", f"Failed to enroll: {r.text}")
            else:
                r = requests.delete(f"{API_URL}/students/{self.student_id}/unenroll/{course_id}")
                if r.status_code == 200:
                    messagebox.showinfo("Success", "Student unenrolled")
                    self.parent.refresh_students()
                    self.destroy()
                else:
                    messagebox.showerror("Error", f"Failed to unenroll: {r.text}")
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Connection Error", "Failed to reach API. Is the server running?")
class CourseTab(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        left = ttk.Frame(self)
        left.pack(side="left", fill="y", padx=10, pady=10)
        ttk.Label(left, text="Title:").pack(anchor="w")
        self.title_entry = ttk.Entry(left, width=30)
        self.title_entry.pack(anchor="w")
        ttk.Label(left, text="Description:").pack(anchor="w")
        self.desc_entry = ttk.Entry(left, width=30)
        self.desc_entry.pack(anchor="w")
        ttk.Label(left, text="Level:").pack(anchor="w")
        self.level_entry = ttk.Entry(left, width=30)
        self.level_entry.pack(anchor="w")
        ttk.Label(left, text="Teacher ID (optional):").pack(anchor="w")
        self.teacher_entry = ttk.Entry(left, width=30)
        self.teacher_entry.pack(anchor="w")
        ttk.Button(left, text="Create Course", command=self.create_course).pack(pady=5)
        ttk.Button(left, text="Refresh List", command=self.refresh_courses).pack(pady=5)
        ttk.Button(left, text="Assign Teacher to Selected Course", command=self.assign_teacher_to_selected).pack(pady=5)
        ttk.Button(left, text="Show Students in Course", command=self.show_course_students).pack(pady=5)
        right = ttk.Frame(self)
        right.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        columns = ("id", "title", "level", "teacher_id")
        self.tree = ttk.Treeview(right, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col.title())
            self.tree.column(col, width=120)
        self.tree.pack(fill="both", expand=True)
        self.refresh_courses()
    def create_course(self):
        title = self.title_entry.get().strip()
        description = self.desc_entry.get().strip()
        level = self.level_entry.get().strip()
        teacher_id = self.teacher_entry.get().strip()
        if not title:
            messagebox.showwarning("Validation", "Title is required")
            return
        payload = {"title": title, "description": description or None, "level": level or None}
        if teacher_id:
            try:
                payload["teacher_id"] = int(teacher_id)
            except ValueError:
                messagebox.showwarning("Validation", "Teacher ID must be an integer")
                return
        try:
            r = requests.post(f"{API_URL}/courses/", json=payload)
            if r.status_code == 201:
                messagebox.showinfo("Success", "Course created")
                self.title_entry.delete(0, tk.END)
                self.desc_entry.delete(0, tk.END)
                self.level_entry.delete(0, tk.END)
                self.teacher_entry.delete(0, tk.END)
                self.refresh_courses()
            else:
                messagebox.showerror("Error", f"Failed to create course: {r.text}")
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Connection Error", "Failed to reach API. Is the server running?")
    def refresh_courses(self):
        try:
            r = requests.get(f"{API_URL}/courses/")
            if r.status_code == 200:
                for i in self.tree.get_children():
                    self.tree.delete(i)
                for c in r.json():
                    tid = c["teacher"]["id"] if c.get("teacher") else None
                    self.tree.insert("", tk.END, values=(c["id"], c["title"], c.get("level"), tid))
            else:
                messagebox.showerror("Error", f"Failed to list courses: {r.text}")
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Connection Error", "Failed to reach API. Is the server running?")
    def get_selected_course_id(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Selection", "No course selected")
            return None
        item = self.tree.item(sel[0])
        return item["values"][0]
    def assign_teacher_to_selected(self):
        cid = self.get_selected_course_id()
        if not cid:
            return
        # Ask for teacher id
        tid = simple_input_dialog(self, "Assign Teacher", "Enter Teacher ID:")
        if tid is None:
            return
        try:
            tid_int = int(tid)
        except ValueError:
            messagebox.showwarning("Validation", "Teacher ID must be an integer")
            return
        try:
            r = requests.post(f"{API_URL}/courses/{cid}/assign_teacher/{tid_int}")
            if r.status_code == 200:
                messagebox.showinfo("Success", "Teacher assigned to course")
                self.refresh_courses()
            else:
                messagebox.showerror("Error", f"Failed to assign teacher: {r.text}")
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Connection Error", "Failed to reach API. Is the server running?")
    def show_course_students(self):
        cid = self.get_selected_course_id()
        if not cid:
            return
        try:
            r = requests.get(f"{API_URL}/courses/{cid}")
            if r.status_code == 200:
                course = r.json()
                students = course.get("students", [])
                if not students:
                    messagebox.showinfo("Students", "No students enrolled")
                    return
                text = "\n".join([f"{s['id']}: {s['name']} ({s['email']})" for s in students])
                messagebox.showinfo("Students in Course", text)
            else:
                messagebox.showerror("Error", f"Failed to fetch course: {r.text}")
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Connection Error", "Failed to reach API. Is the server running?")
class TeacherTab(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        left = ttk.Frame(self)
        left.pack(side="left", fill="y", padx=10, pady=10)
        ttk.Label(left, text="Name:").pack(anchor="w")
        self.name_entry = ttk.Entry(left, width=30)
        self.name_entry.pack(anchor="w")
        ttk.Label(left, text="Email (optional):").pack(anchor="w")
        self.email_entry = ttk.Entry(left, width=30)
        self.email_entry.pack(anchor="w")
        ttk.Button(left, text="Create Teacher", command=self.create_teacher).pack(pady=5)
        ttk.Button(left, text="Refresh List", command=self.refresh_teachers).pack(pady=5)
        ttk.Button(left, text="Show Teacher Courses", command=self.show_teacher_courses).pack(pady=5)
        right = ttk.Frame(self)
        right.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        columns = ("id", "name", "email")
        self.tree = ttk.Treeview(right, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col.title())
            self.tree.column(col, width=200)
        self.tree.pack(fill="both", expand=True)
        self.refresh_teachers()
    def create_teacher(self):
        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()
        if not name:
            messagebox.showwarning("Validation", "Name is required")
            return
        payload = {"name": name, "email": email or None}
        try:
            r = requests.post(f"{API_URL}/teachers/", json=payload)
            if r.status_code == 201:
                messagebox.showinfo("Success", "Teacher created")
                self.name_entry.delete(0, tk.END)
                self.email_entry.delete(0, tk.END)
                self.refresh_teachers()
            else:
                messagebox.showerror("Error", f"Failed to create teacher: {r.text}")
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Connection Error", "Failed to reach API. Is the server running?")
    def refresh_teachers(self):
        try:
            r = requests.get(f"{API_URL}/teachers/")
            if r.status_code == 200:
                for i in self.tree.get_children():
                    self.tree.delete(i)
                for t in r.json():
                    self.tree.insert("", tk.END, values=(t["id"], t["name"], t.get("email")))
            else:
                messagebox.showerror("Error", f"Failed to list teachers: {r.text}")
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Connection Error", "Failed to reach API. Is the server running?")
    def get_selected_teacher_id(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Selection", "No teacher selected")
            return None
        item = self.tree.item(sel[0])
        return item["values"][0]
    def show_teacher_courses(self):
        tid = self.get_selected_teacher_id()
        if not tid:
            return
        try:
            r = requests.get(f"{API_URL}/teachers/{tid}/courses")
            if r.status_code == 200:
                courses = r.json()
                if not courses:
                    messagebox.showinfo("Courses", "No courses assigned")
                    return
                text = "\n".join([f"{c['id']}: {c['title']} (Level: {c.get('level')})" for c in courses])
                messagebox.showinfo("Teacher Courses", text)
            else:
                messagebox.showerror("Error", f"Failed to fetch teacher courses: {r.text}")
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Connection Error", "Failed to reach API. Is the server running?")
def simple_input_dialog(parent, title, prompt):
    dialog = tk.Toplevel(parent)
    dialog.title(title)
    dialog.geometry("300x120")
    tk.Label(dialog, text=prompt).pack(pady=5)
    entry = ttk.Entry(dialog, width=30)
    entry.pack(pady=5)
    result = {"value": None}
    def on_ok():
        result["value"] = entry.get()
        dialog.destroy()
    def on_cancel():
        dialog.destroy()
    ttk.Button(dialog, text="OK", command=on_ok).pack(side="left", padx=20, pady=10)
    ttk.Button(dialog, text="Cancel", command=on_cancel).pack(side="right", padx=20, pady=10)
    parent.wait_window(dialog)
    return result["value"]
def run_gui():
    app = App()
    app.mainloop()
if __name__ == "__main__":
    # Run GUI in main thread
    run_gui()