"""
SRMS - Student Dashboard
Student view with MLS enforcement (can only see own data)
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.database.connection import get_database, is_sqlserver


class StudentDashboard(ttk.Frame):
    """Student Dashboard - can only view own data (MLS enforced)."""
    
    def __init__(self, parent, user, on_logout, theme=None):
        super().__init__(parent)
        self.user = user
        self.on_logout = on_logout
        self.db = get_database()
        self.theme = theme
        self.student_id = user.get('linked_id')
        
        self._create_layout()
    
    def _create_layout(self):
        """Create dashboard layout."""
        # Header
        self._create_header()
        
        # Create notebook for tabs
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tabs
        self._create_profile_tab(notebook)
        self._create_grades_tab(notebook)
        self._create_attendance_tab(notebook)
        self._create_courses_tab(notebook)
        self._create_role_request_tab(notebook)
    
    def _create_header(self):
        """Create header."""
        header = ttk.Frame(self)
        header.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(header, text="🎓 Student Dashboard", 
                  font=('Segoe UI', 18, 'bold')).pack(side=tk.LEFT)
        
        right_frame = ttk.Frame(header)
        right_frame.pack(side=tk.RIGHT)
        
        ttk.Label(right_frame, text=f"👤 {self.user.get('username', '')} | ", 
                  font=('Segoe UI', 11)).pack(side=tk.LEFT)
        ttk.Label(right_frame, text=f"Clearance: {self.user.get('clearance_level', 1)} | ", 
                  font=('Segoe UI', 11)).pack(side=tk.LEFT)
        ttk.Label(right_frame, text="🔒 MLS: Read Own Data Only", 
                  font=('Segoe UI', 9)).pack(side=tk.LEFT, padx=10)
        ttk.Button(right_frame, text="🚪 Logout", command=self.on_logout).pack(side=tk.LEFT)
        
        ttk.Separator(self, orient='horizontal').pack(fill=tk.X, padx=10)
    
    def _create_profile_tab(self, notebook):
        """Create profile tab."""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="👤 My Profile")
        
        ttk.Label(tab, text="📋 My Profile", font=('Segoe UI', 14, 'bold')).pack(pady=10)
        
        profile_frame = ttk.LabelFrame(tab, text="Personal Information")
        profile_frame.pack(fill=tk.X, padx=20, pady=10)
        
        try:
            if is_sqlserver() and self.student_id:
                student = self.db.fetch_one(
                    "SELECT FullName, Email, Phone_Display, Department, Status, EnrollmentDate "
                    "FROM STUDENT WHERE StudentID = %s",
                    (self.student_id,)
                )
                if student:
                    fields = [
                        ("Name", student.get('FullName', 'N/A')),
                        ("Email", student.get('Email', 'N/A')),
                        ("Phone", student.get('Phone_Display', '***-****')),  # Masked
                        ("Department", student.get('Department', 'N/A')),
                        ("Status", student.get('Status', 'Active')),
                    ]
                    for label, value in fields:
                        row = ttk.Frame(profile_frame)
                        row.pack(fill=tk.X, pady=3, padx=10)
                        ttk.Label(row, text=f"{label}:", font=('Segoe UI', 11, 'bold'), width=15).pack(side=tk.LEFT)
                        ttk.Label(row, text=str(value), font=('Segoe UI', 11)).pack(side=tk.LEFT)
        except Exception as e:
            ttk.Label(profile_frame, text=f"Error loading profile: {e}").pack()
    
    def _create_grades_tab(self, notebook):
        """Create grades tab (published only)."""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="📈 My Grades")
        
        ttk.Label(tab, text="📈 My Grades (Published Only)", 
                  font=('Segoe UI', 14, 'bold')).pack(pady=10)
        
        # Note about MLS
        ttk.Label(tab, text="🔒 MLS Enforcement: You can only see YOUR OWN published grades",
                  font=('Segoe UI', 10)).pack(pady=5)
        
        columns = ('Course', 'Grade', 'Letter', 'Semester')
        tree = ttk.Treeview(tab, columns=columns, show='headings', height=10)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        try:
            if is_sqlserver() and self.student_id:
                grades = self.db.fetch_all("""
                    SELECT c.CourseCode, c.CourseName, g.GradeValue_Display, 
                           g.GradeLetter, g.Semester
                    FROM GRADES g
                    JOIN COURSE c ON g.CourseID = c.CourseID
                    WHERE g.StudentID = %s AND g.IsPublished = 1
                """, (self.student_id,))
                
                for g in grades:
                    tree.insert('', tk.END, values=(
                        f"{g['CourseCode']} - {g['CourseName'][:20]}",
                        g.get('GradeValue_Display', ''),
                        g.get('GradeLetter', ''),
                        g.get('Semester', '')
                    ))
        except Exception as e:
            ttk.Label(tab, text=f"Error: {e}").pack()
        
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
    def _create_attendance_tab(self, notebook):
        """Create attendance tab."""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="📅 Attendance")
        
        ttk.Label(tab, text="📅 My Attendance Records", 
                  font=('Segoe UI', 14, 'bold')).pack(pady=10)
        
        columns = ('Course', 'Date', 'Status')
        tree = ttk.Treeview(tab, columns=columns, show='headings', height=10)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=200)
        
        try:
            if is_sqlserver() and self.student_id:
                attendance = self.db.fetch_all("""
                    SELECT c.CourseCode, a.AttendanceDate, a.StatusText
                    FROM ATTENDANCE a
                    JOIN COURSE c ON a.CourseID = c.CourseID
                    WHERE a.StudentID = %s
                    ORDER BY a.AttendanceDate DESC
                """, (self.student_id,))
                
                for a in attendance:
                    date_str = str(a.get('AttendanceDate', ''))[:10]
                    tree.insert('', tk.END, values=(
                        a['CourseCode'], date_str, a.get('StatusText', '')
                    ))
        except Exception as e:
            ttk.Label(tab, text=f"Error: {e}").pack()
        
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
    def _create_courses_tab(self, notebook):
        """Create enrolled courses tab."""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="📚 My Courses")
        
        ttk.Label(tab, text="📚 My Enrolled Courses", 
                  font=('Segoe UI', 14, 'bold')).pack(pady=10)
        
        columns = ('Code', 'Name', 'Credits', 'Semester')
        tree = ttk.Treeview(tab, columns=columns, show='headings', height=10)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        try:
            if is_sqlserver() and self.student_id:
                courses = self.db.fetch_all("""
                    SELECT c.CourseCode, c.CourseName, c.Credits, ce.Semester
                    FROM COURSE_ENROLLMENT ce
                    JOIN COURSE c ON ce.CourseID = c.CourseID
                    WHERE ce.StudentID = %s
                """, (self.student_id,))
                
                for c in courses:
                    tree.insert('', tk.END, values=(
                        c['CourseCode'], c['CourseName'],
                        c.get('Credits', 3), c.get('Semester', '')
                    ))
        except Exception as e:
            ttk.Label(tab, text=f"Error: {e}").pack()
        
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
    def _create_role_request_tab(self, notebook):
        """Create role upgrade request tab (Part B)."""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="📝 Request Upgrade")
        
        ttk.Label(tab, text="📝 Request Role Upgrade (Part B)", 
                  font=('Segoe UI', 14, 'bold')).pack(pady=10)
        
        current_role = self.user.get('role', 'Student')
        next_role = 'TA' if current_role == 'Student' else 'Instructor' if current_role == 'TA' else None
        
        if not next_role:
            ttk.Label(tab, text="You cannot request further upgrades.", 
                      font=('Segoe UI', 12)).pack(pady=20)
            return
        
        ttk.Label(tab, text=f"Current Role: {current_role}", 
                  font=('Segoe UI', 12)).pack(pady=5)
        ttk.Label(tab, text=f"Requestable Role: {next_role}", 
                  font=('Segoe UI', 12, 'bold')).pack(pady=5)
        
        # Request form
        form = ttk.LabelFrame(tab, text="Submit New Request")
        form.pack(fill=tk.X, padx=20, pady=20)
        
        ttk.Label(form, text="Reason for upgrade request:").pack(anchor='w', padx=10, pady=5)
        reason_text = tk.Text(form, height=5, width=50)
        reason_text.pack(padx=10, pady=5)
        
        def submit_request():
            reason = reason_text.get("1.0", tk.END).strip()
            if not reason:
                messagebox.showwarning("Warning", "Please provide a reason")
                return
            
            try:
                if is_sqlserver():
                    # Use Stored Procedure sp_SubmitRoleRequest
                    self.db.execute(
                        "EXEC usp_SubmitRoleRequest @UserID=%s, @Username=%s, @CurrentRole=%s, "
                        "@RequestedRole=%s, @CurrentClearance=%s, @RequestedClearance=%s, @Reason=%s",
                        (self.user.get('user_id'), self.user.get('username'), 
                         current_role, next_role,
                         self.user.get('clearance_level'), self.user.get('clearance_level') + 1,
                         reason)
                    )
                    self.db.commit()
                    messagebox.showinfo("Success", "Role upgrade request submitted!")
                    reason_text.delete("1.0", tk.END)
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        ttk.Button(form, text="📤 Submit Request", command=submit_request).pack(pady=10)
        
        # Show existing requests
        ttk.Label(tab, text="Your Request History:", 
                  font=('Segoe UI', 11, 'bold')).pack(anchor='w', padx=20, pady=(20, 5))
        
        columns = ('ID', 'From', 'To', 'Status', 'Date')
        tree = ttk.Treeview(tab, columns=columns, show='headings', height=5)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        try:
            if is_sqlserver():
                requests = self.db.fetch_all(
                    "SELECT RequestID, CurrentRole, RequestedRole, Status, DateSubmitted "
                    "FROM ROLE_REQUESTS WHERE UserID = %s ORDER BY DateSubmitted DESC",
                    (self.user.get('user_id'),)
                )
                for r in requests:
                    date_str = str(r.get('DateSubmitted', ''))[:10]
                    tree.insert('', tk.END, values=(
                        r['RequestID'], r['CurrentRole'], r['RequestedRole'],
                        r['Status'], date_str
                    ))
        except:
            pass
        
        tree.pack(fill=tk.X, padx=20, pady=5)
