"""
SRMS - Instructor Dashboard
Instructor view for managing grades and viewing assigned students
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.database.connection import get_database, is_sqlserver


class InstructorDashboard(ttk.Frame):
    """Instructor Dashboard - manage grades for assigned courses."""
    
    def __init__(self, parent, user, on_logout, theme=None):
        super().__init__(parent)
        self.user = user
        self.on_logout = on_logout
        self.db = get_database()
        self.theme = theme
        self.instructor_id = user.get('linked_id')
        
        self._create_layout()
    
    def _create_layout(self):
        """Create dashboard layout."""
        self._create_header()
        
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self._create_overview_tab(notebook)
        self._create_my_courses_tab(notebook)
        self._create_grades_tab(notebook)
        self._create_students_tab(notebook)
        self._create_attendance_tab(notebook)
    
    def _create_header(self):
        """Create header."""
        header = ttk.Frame(self)
        header.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(header, text="👨‍🏫 Instructor Dashboard", 
                  font=('Segoe UI', 18, 'bold')).pack(side=tk.LEFT)
        
        right_frame = ttk.Frame(header)
        right_frame.pack(side=tk.RIGHT)
        
        ttk.Label(right_frame, text=f"👤 {self.user.get('username', '')} | ", 
                  font=('Segoe UI', 11)).pack(side=tk.LEFT)
        ttk.Label(right_frame, text=f"Clearance: {self.user.get('clearance_level', 3)} | ", 
                  font=('Segoe UI', 11)).pack(side=tk.LEFT)
        ttk.Label(right_frame, text="📊 Can: Read Students, Create/Update Grades", 
                  font=('Segoe UI', 9)).pack(side=tk.LEFT, padx=10)
        ttk.Button(right_frame, text="🚪 Logout", command=self.on_logout).pack(side=tk.LEFT)
        
        ttk.Separator(self, orient='horizontal').pack(fill=tk.X, padx=10)
    
    def _create_overview_tab(self, notebook):
        """Create overview tab."""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="📊 Overview")
        
        ttk.Label(tab, text="📊 Instructor Overview", 
                  font=('Segoe UI', 14, 'bold')).pack(pady=10)
        
        # Stats
        stats_frame = ttk.Frame(tab)
        stats_frame.pack(fill=tk.X, padx=20, pady=10)
        
        try:
            if is_sqlserver():
                # Get assigned courses count
                courses = self.db.fetch_one(
                    "SELECT COUNT(*) as c FROM COURSE_ASSIGNMENT WHERE UserID = %s",
                    (self.user.get('user_id'),)
                )
                
                stats = [
                    ("My Courses", courses.get('c', 0) if courses else 0),
                    ("Clearance Level", self.user.get('clearance_level', 3)),
                ]
                
                for label, value in stats:
                    card = ttk.LabelFrame(stats_frame, text=label)
                    card.pack(side=tk.LEFT, padx=20, pady=5, ipadx=30, ipady=10)
                    ttk.Label(card, text=str(value), font=('Segoe UI', 20, 'bold')).pack()
        except:
            pass
        
        # RBAC permissions
        perms_frame = ttk.LabelFrame(tab, text="🔐 Your RBAC Permissions")
        perms_frame.pack(fill=tk.X, padx=20, pady=10)
        
        permissions = [
            ("STUDENT table", "READ only"),
            ("GRADES table", "CREATE, READ, UPDATE"),
            ("ATTENDANCE table", "READ only"),
            ("COURSE table", "READ only"),
            ("USERS table", "DENIED"),
        ]
        
        for table, perm in permissions:
            row = ttk.Frame(perms_frame)
            row.pack(fill=tk.X, pady=2, padx=10)
            ttk.Label(row, text=table, width=20, font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT)
            ttk.Label(row, text=perm, font=('Segoe UI', 10)).pack(side=tk.LEFT)
    
    def _create_my_courses_tab(self, notebook):
        """Create my courses tab."""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="📚 My Courses")
        
        ttk.Label(tab, text="📚 My Assigned Courses", 
                  font=('Segoe UI', 14, 'bold')).pack(pady=10)
        
        columns = ('Code', 'Name', 'Students', 'Semester')
        tree = ttk.Treeview(tab, columns=columns, show='headings', height=10)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        try:
            if is_sqlserver():
                courses = self.db.fetch_all("""
                    SELECT c.CourseCode, c.CourseName, c.Semester,
                           (SELECT COUNT(*) FROM COURSE_ENROLLMENT ce WHERE ce.CourseID = c.CourseID) as StudentCount
                    FROM COURSE c
                    JOIN COURSE_ASSIGNMENT ca ON c.CourseID = ca.CourseID
                    WHERE ca.UserID = %s AND ca.AssignmentType = 'Instructor'
                """, (self.user.get('user_id'),))
                
                for c in courses:
                    tree.insert('', tk.END, values=(
                        c['CourseCode'], c['CourseName'],
                        c.get('StudentCount', 0), c.get('Semester', '')
                    ))
        except Exception as e:
            ttk.Label(tab, text=f"Error: {e}").pack()
        
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
    def _create_grades_tab(self, notebook):
        """Create grades tab - can add/edit grades."""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="📈 Grades")
        
        ttk.Label(tab, text="📈 Manage Grades (Your Courses)", 
                  font=('Segoe UI', 14, 'bold')).pack(pady=10)
        
        # Add grade form
        form = ttk.LabelFrame(tab, text="Add/Update Grade")
        form.pack(fill=tk.X, padx=10, pady=10)
        
        # Get my courses for dropdown
        course_ids = []
        try:
            if is_sqlserver():
                courses = self.db.fetch_all("""
                    SELECT c.CourseID, c.CourseCode FROM COURSE c
                    JOIN COURSE_ASSIGNMENT ca ON c.CourseID = ca.CourseID
                    WHERE ca.UserID = %s
                """, (self.user.get('user_id'),))
                course_ids = [(c['CourseID'], c['CourseCode']) for c in courses]
        except:
            pass
        
        form_row1 = ttk.Frame(form)
        form_row1.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(form_row1, text="Course:").pack(side=tk.LEFT)
        course_var = tk.StringVar()
        course_combo = ttk.Combobox(form_row1, textvariable=course_var, width=15,
                                     values=[f"{c[1]}" for c in course_ids])
        course_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(form_row1, text="Student ID:").pack(side=tk.LEFT, padx=(20, 0))
        student_var = tk.StringVar()
        ttk.Entry(form_row1, textvariable=student_var, width=10).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(form_row1, text="Grade:").pack(side=tk.LEFT, padx=(20, 0))
        grade_var = tk.StringVar()
        ttk.Entry(form_row1, textvariable=grade_var, width=8).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(form_row1, text="Letter:").pack(side=tk.LEFT, padx=(20, 0))
        letter_var = tk.StringVar()
        ttk.Combobox(form_row1, textvariable=letter_var, width=5,
                     values=['A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D', 'F']).pack(side=tk.LEFT, padx=5)
        
        def add_grade():
            try:
                course_code = course_var.get()
                student_id = int(student_var.get())
                grade_value = float(grade_var.get())
                letter = letter_var.get()
                
                # Get course ID
                course = next((c for c in course_ids if c[1] == course_code), None)
                if not course:
                    messagebox.showerror("Error", "Select a course")
                    return
                
                if is_sqlserver():
                    self.db.execute("""
                        INSERT INTO GRADES (StudentID, CourseID, GradeValue_Display, GradeLetter, 
                                           Semester, EnteredBy, IsPublished, ClassificationLevel)
                        VALUES (%s, %s, %s, %s, 'Fall', %s, 0, 3)
                    """, (student_id, course[0], grade_value, letter, self.instructor_id))
                    self.db.commit()
                    messagebox.showinfo("Success", "Grade added!")
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        ttk.Button(form_row1, text="Add Grade", command=add_grade).pack(side=tk.LEFT, padx=20)
        
        # Grades list
        columns = ('ID', 'Student', 'Course', 'Grade', 'Letter', 'Published')
        self.grades_tree = ttk.Treeview(tab, columns=columns, show='headings', height=10)
        
        for col in columns:
            self.grades_tree.heading(col, text=col)
            self.grades_tree.column(col, width=100)
        
        try:
            if is_sqlserver():
                grades = self.db.fetch_all("""
                    SELECT g.GradeID, s.FullName, c.CourseCode, 
                           g.GradeValue_Display, g.GradeLetter, g.IsPublished
                    FROM GRADES g
                    JOIN STUDENT s ON g.StudentID = s.StudentID
                    JOIN COURSE c ON g.CourseID = c.CourseID
                    JOIN COURSE_ASSIGNMENT ca ON c.CourseID = ca.CourseID
                    WHERE ca.UserID = %s
                """, (self.user.get('user_id'),))
                
                for g in grades:
                    pub = "✓" if g.get('IsPublished', 0) else "✗"
                    self.grades_tree.insert('', tk.END, values=(
                        g['GradeID'], g['FullName'], g['CourseCode'],
                        g.get('GradeValue_Display', ''), g.get('GradeLetter', ''), pub
                    ))
        except Exception as e:
            ttk.Label(tab, text=f"Error: {e}").pack()
        
        self.grades_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Update Button
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(btn_frame, text="✏️ Update Selected Grade", 
                  command=self._update_grade_dialog).pack(side=tk.RIGHT)
    
    def _create_students_tab(self, notebook):
        """Create students tab."""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="🎓 Students")
        
        ttk.Label(tab, text="🎓 Students in My Courses", 
                  font=('Segoe UI', 14, 'bold')).pack(pady=10)
        
        columns = ('ID', 'Name', 'Email', 'Course')
        tree = ttk.Treeview(tab, columns=columns, show='headings', height=15)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        try:
            if is_sqlserver():
                students = self.db.fetch_all("""
                    SELECT DISTINCT s.StudentID, s.FullName, s.Email, c.CourseCode
                    FROM STUDENT s
                    JOIN COURSE_ENROLLMENT ce ON s.StudentID = ce.StudentID
                    JOIN COURSE c ON ce.CourseID = c.CourseID
                    JOIN COURSE_ASSIGNMENT ca ON c.CourseID = ca.CourseID
                    WHERE ca.UserID = %s
                """, (self.user.get('user_id'),))
                
                for s in students:
                    tree.insert('', tk.END, values=(
                        s['StudentID'], s['FullName'], s['Email'], s['CourseCode']
                    ))
        except Exception as e:
            ttk.Label(tab, text=f"Error: {e}").pack()
        
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
    def _create_attendance_tab(self, notebook):
        """Create attendance tab (read only for instructor)."""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="📅 Attendance")
        
        ttk.Label(tab, text="📅 Attendance (Read Only - TA manages)", 
                  font=('Segoe UI', 14, 'bold')).pack(pady=10)
        
        columns = ('Student', 'Course', 'Date', 'Status')
        tree = ttk.Treeview(tab, columns=columns, show='headings', height=15)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        try:
            if is_sqlserver():
                attendance = self.db.fetch_all("""
                    SELECT s.FullName, c.CourseCode, a.AttendanceDate, a.StatusText
                    FROM ATTENDANCE a
                    JOIN STUDENT s ON a.StudentID = s.StudentID
                    JOIN COURSE c ON a.CourseID = c.CourseID
                    JOIN COURSE_ASSIGNMENT ca ON c.CourseID = ca.CourseID
                    WHERE ca.UserID = %s
                    ORDER BY a.AttendanceDate DESC
                """, (self.user.get('user_id'),))
                
                for a in attendance:
                    date_str = str(a.get('AttendanceDate', ''))[:10]
                    tree.insert('', tk.END, values=(
                        a['FullName'], a['CourseCode'], date_str, a.get('StatusText', '')
                    ))
        except Exception as e:
            ttk.Label(tab, text=f"Error: {e}").pack()
        
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    def _update_grade_dialog(self):
        """Show dialog to update selected grade."""
        selected = self.grades_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a grade to update")
            return
            
        item = self.grades_tree.item(selected[0])
        grade_id = item['values'][0]
        student_name = item['values'][1]
        current_grade = item['values'][3]
        
        dialog = tk.Toplevel(self)
        dialog.title("Update Grade")
        dialog.geometry("300x250")
        
        # Center
        dialog.update_idletasks()
        x = self.winfo_screenwidth() // 2 - 150
        y = self.winfo_screenheight() // 2 - 125
        dialog.geometry(f"+{x}+{y}")
        
        ttk.Label(dialog, text=f"Update Grade for\n{student_name}", 
                 font=('Segoe UI', 12, 'bold'), justify='center').pack(pady=10)
        
        ttk.Label(dialog, text="New Grade Value:").pack(anchor='w', padx=20)
        grade_var = tk.StringVar(value=str(current_grade))
        ttk.Entry(dialog, textvariable=grade_var).pack(fill=tk.X, padx=20, pady=5)
        
        def update():
            try:
                new_val = float(grade_var.get())
                if is_sqlserver():
                    # Use Stored Procedure sp_UpdateGrade
                    self.db.execute(
                        "EXEC usp_UpdateGrade @GradeID=%s, @NewValue=%s, @ExecutorRole='Instructor'",
                        (grade_id, new_val)
                    )
                    self.db.commit()
                    messagebox.showinfo("Success", "Grade updated successfully!")
                    dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update grade:\n{e}")
        
        ttk.Button(dialog, text="Update", command=update).pack(fill=tk.X, padx=20, pady=20)
