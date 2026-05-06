"""
SRMS - Profile Manager
User profile management with password change
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

try:
    import ttkbootstrap as ttk
    from ttkbootstrap.constants import *
    HAS_TTKBOOTSTRAP = True
except ImportError:
    HAS_TTKBOOTSTRAP = False

from src.database.connection import get_database
from src.security.encryption import get_encryption_manager


class ProfileDialog:
    """User profile management dialog."""
    
    def __init__(self, parent, user):
        self.parent = parent
        self.user = user
        self.db = get_database()
        self.encryption = get_encryption_manager()
        
        self._create_dialog()
    
    def _create_dialog(self):
        """Create profile dialog."""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("👤 User Profile")
        self.dialog.geometry("500x600")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Header
        header = ttk.Frame(self.dialog)
        header.pack(fill=tk.X, padx=20, pady=20)
        
        ttk.Label(header, text="👤", font=('Segoe UI', 48)).pack()
        ttk.Label(header, text=self.user['username'], font=('Segoe UI', 18, 'bold')).pack()
        ttk.Label(header, text=f"Role: {self.user['role']} | Clearance: {self.user['clearance_level']}", 
                  font=('Segoe UI', 11)).pack()
        
        # Notebook for tabs
        notebook = ttk.Notebook(self.dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Profile info tab
        self._create_info_tab(notebook)
        
        # Change password tab
        self._create_password_tab(notebook)
        
        # Activity tab
        self._create_activity_tab(notebook)
        
        # Close button
        if HAS_TTKBOOTSTRAP:
            ttk.Button(self.dialog, text="Close", command=self.dialog.destroy, 
                       bootstyle="secondary").pack(pady=20)
        else:
            ttk.Button(self.dialog, text="Close", command=self.dialog.destroy).pack(pady=20)
    
    def _create_info_tab(self, notebook):
        """Create profile info tab."""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="📋 Profile Info")
        
        info_frame = ttk.Frame(tab)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # User info
        info = [
            ("Username", self.user['username']),
            ("Role", self.user['role']),
            ("Clearance Level", f"Level {self.user['clearance_level']}"),
            ("Account Status", "✅ Active" if self.user.get('is_active', True) else "❌ Inactive"),
            ("Last Login", self.user.get('last_login', 'Never')),
            ("Account Created", self.user.get('created_at', 'Unknown')),
        ]
        
        for i, (label, value) in enumerate(info):
            ttk.Label(info_frame, text=f"{label}:", font=('Segoe UI', 11, 'bold')).grid(
                row=i, column=0, sticky='w', pady=5)
            ttk.Label(info_frame, text=str(value), font=('Segoe UI', 11)).grid(
                row=i, column=1, sticky='w', padx=20, pady=5)
        
        # Security info
        security_frame = ttk.Labelframe(tab, text="🔒 Security Info")
        security_frame.pack(fill=tk.X, padx=20, pady=10)
        
        failed_attempts = self.user.get('failed_login_attempts', 0)
        status = "✅ No issues" if failed_attempts == 0 else f"⚠️ {failed_attempts} failed login attempts"
        
        ttk.Label(security_frame, text=f"Security Status: {status}").pack(anchor='w', padx=10, pady=5)
        ttk.Label(security_frame, text="Two-Factor Auth: Not enabled").pack(anchor='w', padx=10, pady=5)
    
    def _create_password_tab(self, notebook):
        """Create change password tab."""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="🔑 Change Password")
        
        form = ttk.Frame(tab)
        form.pack(pady=40)
        
        # Current password
        ttk.Label(form, text="Current Password:").pack(anchor='w', pady=(0, 5))
        self.current_pw = tk.StringVar()
        ttk.Entry(form, textvariable=self.current_pw, show="•", width=30).pack(pady=(0, 15))
        
        # New password
        ttk.Label(form, text="New Password:").pack(anchor='w', pady=(0, 5))
        self.new_pw = tk.StringVar()
        new_entry = ttk.Entry(form, textvariable=self.new_pw, show="•", width=30)
        new_entry.pack(pady=(0, 5))
        
        # Password strength
        self._create_strength_meter(form)
        
        # Confirm password
        ttk.Label(form, text="Confirm New Password:").pack(anchor='w', pady=(15, 5))
        self.confirm_pw = tk.StringVar()
        ttk.Entry(form, textvariable=self.confirm_pw, show="•", width=30).pack(pady=(0, 15))
        
        # Requirements
        req_frame = ttk.Labelframe(form, text="Password Requirements")
        req_frame.pack(fill='x', pady=10)
        
        requirements = [
            "• Minimum 8 characters",
            "• At least one uppercase letter",
            "• At least one number",
            "• At least one special character (!@#$%)"
        ]
        for req in requirements:
            ttk.Label(req_frame, text=req, font=('Segoe UI', 9)).pack(anchor='w', padx=10)
        
        # Change button
        if HAS_TTKBOOTSTRAP:
            ttk.Button(form, text="🔐 Change Password", command=self._change_password,
                       bootstyle="success").pack(pady=20)
        else:
            ttk.Button(form, text="Change Password", command=self._change_password).pack(pady=20)
    
    def _create_strength_meter(self, parent):
        """Create password strength meter."""
        frame = ttk.Frame(parent)
        frame.pack(fill='x', pady=5)
        
        self.strength_var = tk.StringVar(value="")
        self.strength_label = ttk.Label(frame, textvariable=self.strength_var, font=('Segoe UI', 9))
        self.strength_label.pack(side='left')
        
        if HAS_TTKBOOTSTRAP:
            self.strength_bar = ttk.Progressbar(frame, length=150, mode='determinate', 
                                                 bootstyle="success-striped")
        else:
            self.strength_bar = ttk.Progressbar(frame, length=150, mode='determinate')
        self.strength_bar.pack(side='right')
        
        self.new_pw.trace('w', self._update_strength)
    
    def _update_strength(self, *args):
        """Update password strength indicator."""
        password = self.new_pw.get()
        score = 0
        
        if len(password) >= 8: score += 25
        if any(c.isupper() for c in password): score += 25
        if any(c.isdigit() for c in password): score += 25
        if any(c in '!@#$%^&*()_+-=' for c in password): score += 25
        
        self.strength_bar['value'] = score
        
        if score <= 25:
            self.strength_var.set("Weak")
        elif score <= 50:
            self.strength_var.set("Fair")
        elif score <= 75:
            self.strength_var.set("Good")
        else:
            self.strength_var.set("Strong ✓")
    
    def _change_password(self):
        """Handle password change."""
        current = self.current_pw.get()
        new = self.new_pw.get()
        confirm = self.confirm_pw.get()
        
        # Validate current password
        if not self.encryption.verify_password(current, self.user['password_hash']):
            messagebox.showerror("Error", "Current password is incorrect")
            return
        
        # Validate new password
        if len(new) < 8:
            messagebox.showerror("Error", "Password must be at least 8 characters")
            return
        
        if new != confirm:
            messagebox.showerror("Error", "New passwords don't match")
            return
        
        # Update password
        new_hash, new_salt = self.encryption.hash_password(new)
        self.db.execute("""
            UPDATE USERS SET password_hash = ?, salt = ?, updated_at = ?
            WHERE user_id = ?
        """, (new_hash, new_salt, datetime.now(), self.user['user_id']))
        self.db.commit()
        
        # Log activity
        self.db.execute("""
            INSERT INTO AUDIT_LOG (user_id, action, table_name, timestamp)
            VALUES (?, ?, ?, ?)
        """, (self.user['user_id'], 'PASSWORD_CHANGED', 'USERS', datetime.now()))
        self.db.commit()
        
        messagebox.showinfo("Success", "Password changed successfully!")
        self.current_pw.set("")
        self.new_pw.set("")
        self.confirm_pw.set("")
    
    def _create_activity_tab(self, notebook):
        """Create activity log tab."""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="📊 Activity")
        
        ttk.Label(tab, text="Recent Activity", font=('Segoe UI', 12, 'bold')).pack(pady=10)
        
        # Activity list
        cols = ('Time', 'Action')
        tree = ttk.Treeview(tab, columns=cols, show='headings', height=10)
        tree.heading('Time', text='Time')
        tree.heading('Action', text='Action')
        tree.column('Time', width=150)
        tree.column('Action', width=250)
        tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Load activity
        activities = self.db.fetch_all("""
            SELECT timestamp, action FROM AUDIT_LOG 
            WHERE user_id = ? ORDER BY timestamp DESC LIMIT 20
        """, (self.user['user_id'],))
        
        for act in activities:
            tree.insert('', 'end', values=(act['timestamp'], act['action']))
        
        if not activities:
            tree.insert('', 'end', values=('', 'No recent activity'))


class ThemeManager:
    """Manage application themes."""
    
    THEMES = {
        'light': {
            'name': 'flatly',
            'bg': '#ffffff',
            'fg': '#212529',
        },
        'dark': {
            'name': 'darkly',
            'bg': '#222222',
            'fg': '#ffffff',
        },
        'blue': {
            'name': 'superhero',
            'bg': '#2c3e50',
            'fg': '#ffffff',
        },
        'green': {
            'name': 'minty',
            'bg': '#f8f9fa',
            'fg': '#333333',
        }
    }
    
    def __init__(self, root):
        self.root = root
        self.current_theme = 'dark'
    
    def set_theme(self, theme_name):
        """Set application theme."""
        if not HAS_TTKBOOTSTRAP:
            return
        
        if theme_name in self.THEMES:
            self.current_theme = theme_name
            # Theme change requires restart in ttkbootstrap
            return True
        return False
    
    def get_available_themes(self):
        """Get list of available themes."""
        return list(self.THEMES.keys())


class ReportGenerator:
    """Generate various reports."""
    
    def __init__(self):
        self.db = get_database()
    
    def generate_grade_report(self, course_id=None):
        """Generate grade statistics report."""
        if course_id:
            grades = self.db.fetch_all("""
                SELECT g.*, c.course_name, s.full_name FROM GRADES g
                JOIN COURSE c ON g.course_id = c.course_id
                JOIN STUDENT s ON g.student_id = s.student_id
                WHERE g.course_id = ?
            """, (course_id,))
        else:
            grades = self.db.fetch_all("""
                SELECT g.*, c.course_name, s.full_name FROM GRADES g
                JOIN COURSE c ON g.course_id = c.course_id
                JOIN STUDENT s ON g.student_id = s.student_id
            """)
        
        # Calculate statistics
        letter_counts = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}
        for g in grades:
            letter = g['grade_letter'][0] if g['grade_letter'] else 'F'
            if letter in letter_counts:
                letter_counts[letter] += 1
        
        return {
            'total_grades': len(grades),
            'letter_distribution': letter_counts,
            'grades': grades
        }
    
    def generate_attendance_report(self, course_id=None, start_date=None, end_date=None):
        """Generate attendance report."""
        query = """
            SELECT a.*, c.course_name, s.full_name FROM ATTENDANCE a
            JOIN COURSE c ON a.course_id = c.course_id
            JOIN STUDENT s ON a.student_id = s.student_id
            WHERE 1=1
        """
        params = []
        
        if course_id:
            query += " AND a.course_id = ?"
            params.append(course_id)
        
        records = self.db.fetch_all(query, tuple(params))
        
        # Calculate statistics
        status_counts = {'Present': 0, 'Absent': 0, 'Late': 0, 'Excused': 0}
        for r in records:
            if r['status'] in status_counts:
                status_counts[r['status']] += 1
        
        total = len(records)
        attendance_rate = (status_counts['Present'] / total * 100) if total > 0 else 0
        
        return {
            'total_records': total,
            'status_distribution': status_counts,
            'attendance_rate': round(attendance_rate, 1),
            'records': records
        }
    
    def generate_security_report(self):
        """Generate security audit report."""
        # Recent logins
        logins = self.db.fetch_all("""
            SELECT * FROM AUDIT_LOG 
            WHERE action IN ('LOGIN', 'LOGIN_FAILED')
            ORDER BY timestamp DESC LIMIT 50
        """)
        
        # Failed login count
        failed = self.db.fetch_one("""
            SELECT COUNT(*) as count FROM AUDIT_LOG 
            WHERE action = 'LOGIN_FAILED'
        """)['count']
        
        # Successful logins
        successful = self.db.fetch_one("""
            SELECT COUNT(*) as count FROM AUDIT_LOG 
            WHERE action = 'LOGIN'
        """)['count']
        
        # Role changes
        role_changes = self.db.fetch_all("""
            SELECT * FROM AUDIT_LOG 
            WHERE action = 'ROLE_CHANGE'
            ORDER BY timestamp DESC LIMIT 20
        """)
        
        return {
            'total_logins': successful,
            'failed_logins': failed,
            'login_success_rate': round(successful / (successful + failed) * 100, 1) if (successful + failed) > 0 else 100,
            'recent_logins': logins,
            'role_changes': role_changes
        }
    
    def export_report_csv(self, report_type, filename):
        """Export report to CSV."""
        import csv
        
        if report_type == 'grades':
            report = self.generate_grade_report()
            data = report['grades']
            headers = ['Student', 'Course', 'Grade', 'Letter', 'Published']
        elif report_type == 'attendance':
            report = self.generate_attendance_report()
            data = report['records']
            headers = ['Student', 'Course', 'Date', 'Status']
        else:
            return False
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            for row in data:
                if report_type == 'grades':
                    writer.writerow([row['full_name'], row['course_name'], 
                                    '[ENCRYPTED]', row['grade_letter'], row['is_published']])
                else:
                    writer.writerow([row['full_name'], row['course_name'],
                                    row['attendance_date'], row['status']])
        
        return True
