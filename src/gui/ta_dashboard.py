"""
SRMS - TA Dashboard
TA view for managing attendance (assigned courses only)
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.database.connection import get_database, is_sqlserver


class TADashboard(ttk.Frame):
    """TA Dashboard - manage attendance for assigned courses."""
    
    def __init__(self, parent, user, on_logout, theme=None):
        super().__init__(parent)
        self.user = user
        self.on_logout = on_logout
        self.db = get_database()
        self.theme = theme
        
        self._create_layout()
    
    def _create_layout(self):
        """Create dashboard layout."""
        self._create_header()
        
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self._create_overview_tab(notebook)
        self._create_attendance_tab(notebook)
        self._create_students_tab(notebook)
        self._create_role_request_tab(notebook)
    
    def _create_header(self):
        """Create header."""
        header = ttk.Frame(self)
        header.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(header, text="📋 TA Dashboard", 
                  font=('Segoe UI', 18, 'bold')).pack(side=tk.LEFT)
        
        right_frame = ttk.Frame(header)
        right_frame.pack(side=tk.RIGHT)
        
        ttk.Label(right_frame, text=f"👤 {self.user.get('username', '')} | ", 
                  font=('Segoe UI', 11)).pack(side=tk.LEFT)
        ttk.Label(right_frame, text=f"Clearance: {self.user.get('clearance_level', 2)} | ", 
                  font=('Segoe UI', 11)).pack(side=tk.LEFT)
        ttk.Label(right_frame, text="📊 Can: Manage Attendance (No Grades)", 
                  font=('Segoe UI', 9)).pack(side=tk.LEFT, padx=10)
        ttk.Button(right_frame, text="🚪 Logout", command=self.on_logout).pack(side=tk.LEFT)
        
        ttk.Separator(self, orient='horizontal').pack(fill=tk.X, padx=10)
    
    def _create_overview_tab(self, notebook):
        """Create overview tab."""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="📊 Overview")
        
        ttk.Label(tab, text="📊 TA Overview", 
                  font=('Segoe UI', 14, 'bold')).pack(pady=10)
        
        # RBAC permissions
        perms_frame = ttk.LabelFrame(tab, text="🔐 Your RBAC Permissions")
        perms_frame.pack(fill=tk.X, padx=20, pady=10)
        
        permissions = [
            ("STUDENT table", "READ (assigned courses only)"),
            ("GRADES table", "DENIED - Instructors only"),
            ("ATTENDANCE table", "CREATE, READ, UPDATE"),
            ("COURSE table", "READ only"),
            ("USERS table", "DENIED"),
        ]
        
        for table, perm in permissions:
            row = ttk.Frame(perms_frame)
            row.pack(fill=tk.X, pady=2, padx=10)
            ttk.Label(row, text=table, width=20, font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT)
            color = 'green' if 'CREATE' in perm else 'gray'
            ttk.Label(row, text=perm, font=('Segoe UI', 10)).pack(side=tk.LEFT)
        
        # Inference control note
        ttk.Label(tab, text="⚠️ Inference Control: You can only see students in YOUR assigned courses",
                  font=('Segoe UI', 10)).pack(pady=10)
    
    def _create_attendance_tab(self, notebook):
        """Create attendance management tab."""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="📅 Attendance")
        
        ttk.Label(tab, text="📅 Manage Attendance", 
                  font=('Segoe UI', 14, 'bold')).pack(pady=10)
        
        # Add attendance form
        form = ttk.LabelFrame(tab, text="Record Attendance")
        form.pack(fill=tk.X, padx=10, pady=10)
        
        # Get assigned courses
        course_ids = []
        try:
            if is_sqlserver():
                courses = self.db.fetch_all("""
                    SELECT c.CourseID, c.CourseCode FROM COURSE c
                    JOIN COURSE_ASSIGNMENT ca ON c.CourseID = ca.CourseID
                    WHERE ca.UserID = %s AND ca.AssignmentType = 'TA'
                """, (self.user.get('user_id'),))
                course_ids = [(c['CourseID'], c['CourseCode']) for c in courses]
        except:
            pass
        
        form_row = ttk.Frame(form)
        form_row.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(form_row, text="Course:").pack(side=tk.LEFT)
        course_var = tk.StringVar()
        course_combo = ttk.Combobox(form_row, textvariable=course_var, width=12,
                                     values=[c[1] for c in course_ids])
        course_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(form_row, text="Student ID:").pack(side=tk.LEFT, padx=(15, 0))
        student_var = tk.StringVar()
        ttk.Entry(form_row, textvariable=student_var, width=8).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(form_row, text="Status:").pack(side=tk.LEFT, padx=(15, 0))
        status_var = tk.IntVar(value=1)
        ttk.Radiobutton(form_row, text="Present", variable=status_var, value=1).pack(side=tk.LEFT)
        ttk.Radiobutton(form_row, text="Absent", variable=status_var, value=0).pack(side=tk.LEFT)
        
        def record_attendance():
            try:
                course_code = course_var.get()
                student_id = int(student_var.get())
                status = status_var.get()
                
                course = next((c for c in course_ids if c[1] == course_code), None)
                if not course:
                    messagebox.showerror("Error", "Select a course")
                    return
                
                if is_sqlserver():
                    # Use Stored Procedure sp_UpdateAttendance
                    self.db.execute(
                        "EXEC usp_UpdateAttendance @StudentID=%s, @CourseID=%s, @Status=%s, @ExecutorID=%s, @ExecutorRole='TA'",
                        (student_id, course[0], status, self.user.get('user_id'))
                    )
                    self.db.commit()
                    messagebox.showinfo("Success", "Attendance recorded!")
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        ttk.Button(form_row, text="Record", command=record_attendance).pack(side=tk.LEFT, padx=20)
        
        # Attendance list
        columns = ('ID', 'Student', 'Course', 'Date', 'Status')
        tree = ttk.Treeview(tab, columns=columns, show='headings', height=12)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        
        try:
            if is_sqlserver():
                attendance = self.db.fetch_all("""
                    SELECT a.AttendanceID, s.FullName, c.CourseCode, 
                           a.AttendanceDate, a.StatusText
                    FROM ATTENDANCE a
                    JOIN STUDENT s ON a.StudentID = s.StudentID
                    JOIN COURSE c ON a.CourseID = c.CourseID
                    JOIN COURSE_ASSIGNMENT ca ON c.CourseID = ca.CourseID
                    WHERE ca.UserID = %s AND ca.AssignmentType = 'TA'
                    ORDER BY a.AttendanceDate DESC
                """, (self.user.get('user_id'),))
                
                for a in attendance:
                    date_str = str(a.get('AttendanceDate', ''))[:10]
                    tree.insert('', tk.END, values=(
                        a['AttendanceID'], a['FullName'], a['CourseCode'],
                        date_str, a.get('StatusText', '')
                    ))
        except Exception as e:
            ttk.Label(tab, text=f"Error: {e}").pack()
        
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
    def _create_students_tab(self, notebook):
        """Create students tab (restricted view)."""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="🎓 Students")
        
        ttk.Label(tab, text="🎓 Students (Assigned Courses Only - Inference Control)", 
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
                    WHERE ca.UserID = %s AND ca.AssignmentType = 'TA'
                """, (self.user.get('user_id'),))
                
                for s in students:
                    tree.insert('', tk.END, values=(
                        s['StudentID'], s['FullName'], s['Email'], s['CourseCode']
                    ))
        except Exception as e:
            ttk.Label(tab, text=f"Error: {e}").pack()
        
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
    def _create_role_request_tab(self, notebook):
        """Create role upgrade request tab."""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="📝 Request Upgrade")
        
        ttk.Label(tab, text="📝 Request Role Upgrade to Instructor", 
                  font=('Segoe UI', 14, 'bold')).pack(pady=10)
        
        ttk.Label(tab, text="Current Role: TA (Clearance 2)", 
                  font=('Segoe UI', 12)).pack(pady=5)
        ttk.Label(tab, text="Requestable: Instructor (Clearance 3)", 
                  font=('Segoe UI', 12, 'bold')).pack(pady=5)
        
        form = ttk.LabelFrame(tab, text="Submit Request")
        form.pack(fill=tk.X, padx=20, pady=20)
        
        ttk.Label(form, text="Reason:").pack(anchor='w', padx=10, pady=5)
        reason_text = tk.Text(form, height=4, width=50)
        reason_text.pack(padx=10, pady=5)
        
        def submit():
            reason = reason_text.get("1.0", tk.END).strip()
            if not reason:
                messagebox.showwarning("Warning", "Provide a reason")
                return
            
            try:
                if is_sqlserver():
                    # Use Stored Procedure sp_SubmitRoleRequest
                    self.db.execute(
                        "EXEC usp_SubmitRoleRequest @UserID=%s, @Username=%s, @CurrentRole='TA', "
                        "@RequestedRole='Instructor', @CurrentClearance=2, @RequestedClearance=3, @Reason=%s",
                        (self.user.get('user_id'), self.user.get('username'), reason)
                    )
                    self.db.commit()
                    messagebox.showinfo("Success", "Request submitted!")
                    reason_text.delete("1.0", tk.END)
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        ttk.Button(form, text="Submit Request", command=submit).pack(pady=10)
