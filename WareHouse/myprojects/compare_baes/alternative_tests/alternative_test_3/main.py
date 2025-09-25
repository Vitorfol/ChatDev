'''
Tkinter GUI client that interacts with the FastAPI backend via HTTP.
Provides forms to create/list Students, Teachers, Courses,
and manage enrollments (Student <-> Course).
'''
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import requests
API_URL = "http://127.0.0.1:8000"
class ApiError(Exception):
    """
    Simple wrapper for API errors.
    """
    pass
class SchoolGUI(tk.Tk):
    """
    Main GUI application window with tabs for Students, Teachers, Courses, and Enrollments.
    """
    def __init__(self):
        super().__init__()
        self.title("School Management Client")
        self.geometry("900x600")
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        self.student_tab = StudentTab(self.notebook)
        self.teacher_tab = TeacherTab(self.notebook)
        self.course_tab = CourseTab(self.notebook)
        self.enrollment_tab = EnrollmentTab(self.notebook)
        self.notebook.add(self.student_tab, text="Students")
        self.notebook.add(self.teacher_tab, text="Teachers")
        self.notebook.add(self.course_tab, text="Courses")
        self.notebook.add(self.enrollment_tab, text="Enrollments")
class StudentTab(ttk.Frame):
    """
    Tab for student CRUD operations.
    """
    def __init__(self, container):
        super().__init__(container)
        # Form to create student
        form_frame = ttk.LabelFrame(self, text="Create Student")
        form_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(form_frame, text="Name:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.name_entry = ttk.Entry(form_frame, width=40)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(form_frame, text="Email:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.email_entry = ttk.Entry(form_frame, width=40)
        self.email_entry.grid(row=1, column=1, padx=5, pady=5)
        create_btn = ttk.Button(form_frame, text="Create", command=self.create_student)
        create_btn.grid(row=2, column=0, columnspan=2, pady=5)
        # List and actions
        list_frame = ttk.LabelFrame(self, text="Students")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.tree = ttk.Treeview(list_frame, columns=("id", "name", "email"), show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Name")
        self.tree.heading("email", text="Email")
        self.tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Button(btn_frame, text="Refresh", command=self.refresh_list).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Delete Selected", command=self.delete_selected).pack(side=tk.LEFT, padx=5)
        self.refresh_list()
    def create_student(self):
        """
        Call API to create a student.
        """
        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()
        if not name or not email:
            messagebox.showwarning("Validation", "Name and email are required.")
            return
        payload = {"name": name, "email": email}
        try:
            resp = requests.post(f"{API_URL}/students/", json=payload)
            resp.raise_for_status()
            messagebox.showinfo("Success", f"Created student: {resp.json()['name']}")
            self.name_entry.delete(0, tk.END)
            self.email_entry.delete(0, tk.END)
            self.refresh_list()
        except requests.HTTPError as e:
            # show server error message if available
            try:
                message = resp.json().get("detail", resp.text)
            except Exception:
                message = resp.text
            messagebox.showerror("Error", f"Failed to create student: {message}")
        except requests.RequestException:
            messagebox.showerror("Error", "Failed to create student. Could not reach API.")
    def refresh_list(self):
        """
        Reload students from API.
        """
        try:
            resp = requests.get(f"{API_URL}/students/")
            resp.raise_for_status()
            students = resp.json()
        except requests.RequestException:
            messagebox.showerror("Error", "Could not reach API. Make sure server is running.")
            return
        for row in self.tree.get_children():
            self.tree.delete(row)
        for s in students:
            self.tree.insert("", tk.END, values=(s["id"], s["name"], s["email"]))
    def delete_selected(self):
        """
        Delete selected student.
        """
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Info", "No student selected.")
            return
        item = self.tree.item(selected[0])
        student_id = item["values"][0]
        if not messagebox.askyesno("Confirm", f"Delete student ID {student_id}?"):
            return
        try:
            resp = requests.delete(f"{API_URL}/students/{student_id}")
            resp.raise_for_status()
            messagebox.showinfo("Deleted", "Student deleted.")
            self.refresh_list()
        except requests.RequestException:
            messagebox.showerror("Error", "Failed to delete student.")
class TeacherTab(ttk.Frame):
    """
    Tab for teacher CRUD operations.
    """
    def __init__(self, container):
        super().__init__(container)
        # Create teacher form
        form_frame = ttk.LabelFrame(self, text="Create Teacher")
        form_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(form_frame, text="Name:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.name_entry = ttk.Entry(form_frame, width=40)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)
        create_btn = ttk.Button(form_frame, text="Create", command=self.create_teacher)
        create_btn.grid(row=1, column=0, columnspan=2, pady=5)
        # List
        list_frame = ttk.LabelFrame(self, text="Teachers")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.tree = ttk.Treeview(list_frame, columns=("id", "name"), show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Name")
        self.tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Button(btn_frame, text="Refresh", command=self.refresh_list).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Delete Selected", command=self.delete_selected).pack(side=tk.LEFT, padx=5)
        self.refresh_list()
    def create_teacher(self):
        """
        Create teacher via API.
        """
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning("Validation", "Name required.")
            return
        payload = {"name": name}
        try:
            resp = requests.post(f"{API_URL}/teachers/", json=payload)
            resp.raise_for_status()
            messagebox.showinfo("Success", f"Created teacher: {resp.json()['name']}")
            self.name_entry.delete(0, tk.END)
            self.refresh_list()
        except requests.RequestException:
            messagebox.showerror("Error", "Failed to create teacher.")
    def refresh_list(self):
        """
        Refresh teacher list.
        """
        try:
            resp = requests.get(f"{API_URL}/teachers/")
            resp.raise_for_status()
            teachers = resp.json()
        except requests.RequestException:
            messagebox.showerror("Error", "Could not reach API.")
            return
        for row in self.tree.get_children():
            self.tree.delete(row)
        for t in teachers:
            self.tree.insert("", tk.END, values=(t["id"], t["name"]))
    def delete_selected(self):
        """
        Delete selected teacher.
        """
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Info", "No teacher selected.")
            return
        item = self.tree.item(selected[0])
        tid = item["values"][0]
        if not messagebox.askyesno("Confirm", f"Delete teacher ID {tid}?"):
            return
        try:
            resp = requests.delete(f"{API_URL}/teachers/{tid}")
            resp.raise_for_status()
            messagebox.showinfo("Deleted", "Teacher deleted.")
            self.refresh_list()
        except requests.RequestException:
            messagebox.showerror("Error", "Failed to delete teacher.")
class CourseTab(ttk.Frame):
    """
    Tab for course CRUD operations.
    """
    def __init__(self, container):
        super().__init__(container)
        # Create course form
        form_frame = ttk.LabelFrame(self, text="Create Course")
        form_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(form_frame, text="Title:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.title_entry = ttk.Entry(form_frame, width=40)
        self.title_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(form_frame, text="Level:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.level_entry = ttk.Entry(form_frame, width=40)
        self.level_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Label(form_frame, text="Teacher ID (optional):").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.teacher_id_entry = ttk.Entry(form_frame, width=40)
        self.teacher_id_entry.grid(row=2, column=1, padx=5, pady=5)
        create_btn = ttk.Button(form_frame, text="Create", command=self.create_course)
        create_btn.grid(row=3, column=0, columnspan=2, pady=5)
        # List and actions
        list_frame = ttk.LabelFrame(self, text="Courses")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.tree = ttk.Treeview(list_frame, columns=("id", "title", "level", "teacher"), show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("title", text="Title")
        self.tree.heading("level", text="Level")
        self.tree.heading("teacher", text="Teacher")
        self.tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Button(btn_frame, text="Refresh", command=self.refresh_list).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Delete Selected", command=self.delete_selected).pack(side=tk.LEFT, padx=5)
        self.refresh_list()
    def create_course(self):
        """
        Create course via API.
        """
        title = self.title_entry.get().strip()
        level = self.level_entry.get().strip()
        teacher_id = self.teacher_id_entry.get().strip()
        if not title or not level:
            messagebox.showwarning("Validation", "Title and level are required.")
            return
        payload = {"title": title, "level": level}
        if teacher_id:
            try:
                payload["teacher_id"] = int(teacher_id)
            except ValueError:
                messagebox.showwarning("Validation", "Teacher ID must be an integer.")
                return
        try:
            resp = requests.post(f"{API_URL}/courses/", json=payload)
            if resp.status_code == 404:
                messagebox.showerror("Error", f"{resp.text}")
                return
            resp.raise_for_status()
            messagebox.showinfo("Success", f"Created course: {resp.json()['title']}")
            self.title_entry.delete(0, tk.END)
            self.level_entry.delete(0, tk.END)
            self.teacher_id_entry.delete(0, tk.END)
            self.refresh_list()
        except requests.RequestException:
            messagebox.showerror("Error", "Failed to create course.")
    def refresh_list(self):
        """
        Refresh courses listing.
        """
        try:
            resp = requests.get(f"{API_URL}/courses/")
            resp.raise_for_status()
            courses = resp.json()
        except requests.RequestException:
            messagebox.showerror("Error", "Could not reach API.")
            return
        for row in self.tree.get_children():
            self.tree.delete(row)
        for c in courses:
            teacher_name = c["teacher"]["name"] if c.get("teacher") else ""
            self.tree.insert("", tk.END, values=(c["id"], c["title"], c["level"], teacher_name))
    def delete_selected(self):
        """
        Delete selected course.
        """
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Info", "No course selected.")
            return
        item = self.tree.item(selected[0])
        cid = item["values"][0]
        if not messagebox.askyesno("Confirm", f"Delete course ID {cid}?"):
            return
        try:
            resp = requests.delete(f"{API_URL}/courses/{cid}")
            resp.raise_for_status()
            messagebox.showinfo("Deleted", "Course deleted.")
            self.refresh_list()
        except requests.RequestException:
            messagebox.showerror("Error", "Failed to delete course.")
class EnrollmentTab(ttk.Frame):
    """
    Tab to manage enrollments (Student <-> Course) and view enrollments.
    """
    def __init__(self, container):
        super().__init__(container)
        top_frame = ttk.LabelFrame(self, text="Enroll / Unenroll")
        top_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(top_frame, text="Course ID:").grid(row=0, column=0, padx=5, pady=5)
        self.course_entry = ttk.Entry(top_frame, width=20)
        self.course_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(top_frame, text="Student ID:").grid(row=1, column=0, padx=5, pady=5)
        self.student_entry = ttk.Entry(top_frame, width=20)
        self.student_entry.grid(row=1, column=1, padx=5, pady=5)
        btn_frame = ttk.Frame(top_frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=5)
        ttk.Button(btn_frame, text="Enroll", command=self.enroll).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Unenroll", command=self.unenroll).pack(side=tk.LEFT, padx=5)
        # Lower frame to list enrollments
        list_frame = ttk.LabelFrame(self, text="View Enrollments")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        # Left: students in course
        left_frame = ttk.Frame(list_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        ttk.Label(left_frame, text="Students in Course (enter Course ID and click View)").pack(anchor=tk.W)
        self.students_text = tk.Text(left_frame, width=40)
        self.students_text.pack(fill=tk.BOTH, expand=True)
        # Right: courses for student
        right_frame = ttk.Frame(list_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        ttk.Label(right_frame, text="Courses for Student (enter Student ID and click View)").pack(anchor=tk.W)
        self.courses_text = tk.Text(right_frame, width=40)
        self.courses_text.pack(fill=tk.BOTH, expand=True)
        # Buttons to view
        view_frame = ttk.Frame(self)
        view_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Button(view_frame, text="View Students in Course", command=self.view_students_in_course).pack(side=tk.LEFT, padx=5)
        ttk.Button(view_frame, text="View Courses for Student", command=self.view_courses_for_student).pack(side=tk.LEFT, padx=5)
    def enroll(self):
        """
        Enroll student to course via API.
        """
        course_id = self.course_entry.get().strip()
        student_id = self.student_entry.get().strip()
        if not course_id or not student_id:
            messagebox.showwarning("Validation", "Course ID and Student ID required.")
            return
        try:
            resp = requests.post(f"{API_URL}/courses/{int(course_id)}/enroll/{int(student_id)}")
            if resp.status_code == 404:
                messagebox.showerror("Error", resp.text)
                return
            resp.raise_for_status()
            messagebox.showinfo("Success", "Student enrolled.")
        except requests.RequestException:
            messagebox.showerror("Error", "Failed to enroll.")
    def unenroll(self):
        """
        Unenroll student from course via API.
        """
        course_id = self.course_entry.get().strip()
        student_id = self.student_entry.get().strip()
        if not course_id or not student_id:
            messagebox.showwarning("Validation", "Course ID and Student ID required.")
            return
        try:
            resp = requests.delete(f"{API_URL}/courses/{int(course_id)}/unenroll/{int(student_id)}")
            if resp.status_code == 404:
                messagebox.showerror("Error", resp.text)
                return
            resp.raise_for_status()
            messagebox.showinfo("Success", "Student unenrolled.")
        except requests.RequestException:
            messagebox.showerror("Error", "Failed to unenroll.")
    def view_students_in_course(self):
        """
        Display students in a given course.
        """
        course_id = self.course_entry.get().strip()
        if not course_id:
            messagebox.showwarning("Validation", "Course ID required.")
            return
        try:
            resp = requests.get(f"{API_URL}/courses/{int(course_id)}/students")
            if resp.status_code == 404:
                messagebox.showerror("Error", resp.text)
                return
            resp.raise_for_status()
            students = resp.json()
            self.students_text.delete(1.0, tk.END)
            if not students:
                self.students_text.insert(tk.END, "(No students enrolled)\n")
                return
            for s in students:
                self.students_text.insert(tk.END, f"ID: {s['id']} Name: {s['name']} Email: {s['email']}\n")
        except requests.RequestException:
            messagebox.showerror("Error", "Failed to fetch students.")
    def view_courses_for_student(self):
        """
        Display courses a given student is enrolled in.
        """
        student_id = self.student_entry.get().strip()
        if not student_id:
            messagebox.showwarning("Validation", "Student ID required.")
            return
        try:
            resp = requests.get(f"{API_URL}/students/{int(student_id)}/courses")
            if resp.status_code == 404:
                messagebox.showerror("Error", resp.text)
                return
            resp.raise_for_status()
            courses = resp.json()
            self.courses_text.delete(1.0, tk.END)
            if not courses:
                self.courses_text.insert(tk.END, "(No courses enrolled)\n")
                return
            for c in courses:
                teacher = c.get("teacher")
                teacher_name = teacher["name"] if teacher else "(no teacher)"
                self.courses_text.insert(tk.END, f"ID: {c['id']} Title: {c['title']} Level: {c['level']} Teacher: {teacher_name}\n")
        except requests.RequestException:
            messagebox.showerror("Error", "Failed to fetch courses.")
def run_gui():
    """
    Launch the Tkinter GUI. This should be run after the API server is running.
    Runs in main thread (Tk requirement).
    """
    app = SchoolGUI()
    app.mainloop()
if __name__ == "__main__":
    """
    If executed directly, start GUI. Ensure that the FastAPI server is running separately.
    """
    run_gui()