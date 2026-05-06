"""
SRMS - Analytics Dashboard
Visual analytics and statistics
"""

import sys
import os
import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

try:
    import ttkbootstrap as ttk
    from ttkbootstrap.constants import *
    HAS_TTKBOOTSTRAP = True
except ImportError:
    HAS_TTKBOOTSTRAP = False

from src.database.connection import get_database


class AnalyticsDashboard(ttk.Frame):
    """Analytics and statistics dashboard."""
    
    def __init__(self, parent, user):
        super().__init__(parent)
        self.user = user
        self.db = get_database()
        
        self._create_widgets()
        self._load_data()
    
    def _create_widgets(self):
        """Create analytics widgets."""
        # Header
        header = ttk.Frame(self)
        header.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(header, text="📊 Analytics Dashboard", font=('Segoe UI', 18, 'bold')).pack(side=tk.LEFT)
        
        if HAS_TTKBOOTSTRAP:
            ttk.Button(header, text="🔄 Refresh", command=self._load_data, 
                       bootstyle="info-outline").pack(side=tk.RIGHT)
        else:
            ttk.Button(header, text="Refresh", command=self._load_data).pack(side=tk.RIGHT)
        
        # Main content with two columns
        main = ttk.Frame(self)
        main.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left column - Stats
        left = ttk.Frame(main)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # Summary cards
        self.cards_frame = ttk.Frame(left)
        self.cards_frame.pack(fill=tk.X, pady=10)
        
        self.cards = {}
        cards_config = [
            ('users', '👥', 'Total Users', 'primary'),
            ('students', '🎓', 'Students', 'info'),
            ('courses', '📚', 'Courses', 'success'),
            ('grades', '📊', 'Grades', 'warning'),
        ]
        
        for i, (key, icon, label, style) in enumerate(cards_config):
            card = self._create_card(self.cards_frame, icon, label, "0")
            card.grid(row=0, column=i, padx=5, pady=5, sticky='nsew')
            self.cards[key] = card
            self.cards_frame.columnconfigure(i, weight=1)
        
        # Grade distribution
        grade_frame = ttk.Labelframe(left, text="📊 Grade Distribution")
        grade_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.grade_canvas = tk.Canvas(grade_frame, height=200, bg='white')
        self.grade_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Attendance chart
        att_frame = ttk.Labelframe(left, text="📅 Attendance Summary")
        att_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.att_canvas = tk.Canvas(att_frame, height=200, bg='white')
        self.att_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Right column - Recent activity
        right = ttk.Frame(main)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        # Recent logins
        login_frame = ttk.Labelframe(right, text="🔐 Recent Logins")
        login_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        cols = ('User', 'Time', 'Status')
        self.login_tree = ttk.Treeview(login_frame, columns=cols, show='headings', height=6)
        for col in cols:
            self.login_tree.heading(col, text=col)
            self.login_tree.column(col, width=100)
        self.login_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Recent activity
        activity_frame = ttk.Labelframe(right, text="📋 Recent Activity")
        activity_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        cols = ('Time', 'User', 'Action')
        self.activity_tree = ttk.Treeview(activity_frame, columns=cols, show='headings', height=8)
        for col in cols:
            self.activity_tree.heading(col, text=col)
            self.activity_tree.column(col, width=100)
        self.activity_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def _create_card(self, parent, icon, label, value):
        """Create a stat card."""
        if HAS_TTKBOOTSTRAP:
            card = ttk.Frame(parent, bootstyle="dark")
        else:
            card = ttk.Frame(parent, relief='raised', borderwidth=2)
        
        ttk.Label(card, text=icon, font=('Segoe UI', 20)).pack(pady=(10, 5))
        value_label = ttk.Label(card, text=value, font=('Segoe UI', 24, 'bold'))
        value_label.pack()
        ttk.Label(card, text=label, font=('Segoe UI', 10)).pack(pady=(5, 10))
        
        card.value_label = value_label
        return card
    
    def _load_data(self):
        """Load analytics data."""
        # Load stats
        user_count = self.db.fetch_one("SELECT COUNT(*) as c FROM USERS")['c']
        student_count = self.db.fetch_one("SELECT COUNT(*) as c FROM STUDENT")['c']
        course_count = self.db.fetch_one("SELECT COUNT(*) as c FROM COURSE")['c']
        grade_count = self.db.fetch_one("SELECT COUNT(*) as c FROM GRADES")['c']
        
        self.cards['users'].value_label.config(text=str(user_count))
        self.cards['students'].value_label.config(text=str(student_count))
        self.cards['courses'].value_label.config(text=str(course_count))
        self.cards['grades'].value_label.config(text=str(grade_count))
        
        # Draw grade distribution
        self._draw_grade_chart()
        
        # Draw attendance chart
        self._draw_attendance_chart()
        
        # Load recent logins
        self._load_recent_logins()
        
        # Load recent activity
        self._load_recent_activity()
    
    def _draw_grade_chart(self):
        """Draw grade distribution bar chart."""
        self.grade_canvas.delete('all')
        
        # Get grade distribution
        grades = self.db.fetch_all("""
            SELECT grade_letter, COUNT(*) as count FROM GRADES 
            GROUP BY grade_letter
        """)
        
        grade_counts = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}
        for g in grades:
            letter = g['grade_letter'][0] if g['grade_letter'] else 'F'
            if letter in grade_counts:
                grade_counts[letter] += g['count']
        
        # Draw bars
        colors = {'A': '#28a745', 'B': '#17a2b8', 'C': '#ffc107', 'D': '#fd7e14', 'F': '#dc3545'}
        max_count = max(grade_counts.values()) if any(grade_counts.values()) else 1
        
        canvas_width = self.grade_canvas.winfo_width() or 400
        canvas_height = self.grade_canvas.winfo_height() or 180
        
        bar_width = 50
        spacing = 20
        start_x = 50
        
        for i, (letter, count) in enumerate(grade_counts.items()):
            x = start_x + i * (bar_width + spacing)
            bar_height = (count / max_count) * (canvas_height - 60) if max_count > 0 else 0
            y = canvas_height - 30
            
            # Draw bar
            self.grade_canvas.create_rectangle(
                x, y - bar_height, x + bar_width, y,
                fill=colors[letter], outline=''
            )
            
            # Draw label
            self.grade_canvas.create_text(x + bar_width/2, y + 10, text=letter, font=('Segoe UI', 10, 'bold'))
            
            # Draw count
            self.grade_canvas.create_text(x + bar_width/2, y - bar_height - 10, 
                                          text=str(count), font=('Segoe UI', 9))
    
    def _draw_attendance_chart(self):
        """Draw attendance pie-style chart."""
        self.att_canvas.delete('all')
        
        # Get attendance distribution
        attendance = self.db.fetch_all("""
            SELECT status, COUNT(*) as count FROM ATTENDANCE 
            GROUP BY status
        """)
        
        status_counts = {'Present': 0, 'Absent': 0, 'Late': 0, 'Excused': 0}
        for a in attendance:
            if a['status'] in status_counts:
                status_counts[a['status']] = a['count']
        
        total = sum(status_counts.values())
        if total == 0:
            return
        
        # Draw horizontal bars
        colors = {'Present': '#28a745', 'Absent': '#dc3545', 'Late': '#ffc107', 'Excused': '#17a2b8'}
        
        canvas_width = self.att_canvas.winfo_width() or 400
        y = 30
        
        for status, count in status_counts.items():
            percentage = (count / total * 100) if total > 0 else 0
            bar_width = (percentage / 100) * (canvas_width - 150)
            
            # Draw bar
            self.att_canvas.create_rectangle(100, y, 100 + bar_width, y + 25,
                                              fill=colors[status], outline='')
            
            # Draw label
            self.att_canvas.create_text(50, y + 12, text=status, font=('Segoe UI', 9), anchor='w')
            
            # Draw percentage
            self.att_canvas.create_text(110 + bar_width, y + 12, 
                                         text=f"{percentage:.1f}%", font=('Segoe UI', 9), anchor='w')
            
            y += 40
    
    def _load_recent_logins(self):
        """Load recent login attempts."""
        for item in self.login_tree.get_children():
            self.login_tree.delete(item)
        
        logins = self.db.fetch_all("""
            SELECT a.*, u.username FROM AUDIT_LOG a
            LEFT JOIN USERS u ON a.user_id = u.user_id
            WHERE a.action IN ('LOGIN', 'LOGIN_FAILED')
            ORDER BY a.timestamp DESC LIMIT 10
        """)
        
        for login in logins:
            status = "✅ Success" if login['action'] == 'LOGIN' else "❌ Failed"
            self.login_tree.insert('', 'end', values=(
                login.get('username', 'Unknown'),
                login['timestamp'][:16] if login['timestamp'] else '',
                status
            ))
    
    def _load_recent_activity(self):
        """Load recent activity."""
        for item in self.activity_tree.get_children():
            self.activity_tree.delete(item)
        
        activities = self.db.fetch_all("""
            SELECT a.*, u.username FROM AUDIT_LOG a
            LEFT JOIN USERS u ON a.user_id = u.user_id
            ORDER BY a.timestamp DESC LIMIT 15
        """)
        
        for act in activities:
            self.activity_tree.insert('', 'end', values=(
                act['timestamp'][:16] if act['timestamp'] else '',
                act.get('username', 'System'),
                act['action']
            ))


class SettingsPage(ttk.Frame):
    """System settings page for admin."""
    
    def __init__(self, parent, user):
        super().__init__(parent)
        self.user = user
        self.db = get_database()
        
        self._create_widgets()
        self._load_settings()
    
    def _create_widgets(self):
        """Create settings widgets."""
        # Header
        header = ttk.Frame(self)
        header.pack(fill=tk.X, padx=20, pady=20)
        
        ttk.Label(header, text="⚙️ System Settings", font=('Segoe UI', 18, 'bold')).pack(side=tk.LEFT)
        
        if HAS_TTKBOOTSTRAP:
            ttk.Button(header, text="💾 Save All", command=self._save_settings,
                       bootstyle="success").pack(side=tk.RIGHT)
        else:
            ttk.Button(header, text="Save All", command=self._save_settings).pack(side=tk.RIGHT)
        
        # Settings notebook
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Security settings
        self._create_security_settings(notebook)
        
        # System settings
        self._create_system_settings(notebook)
        
        # About
        self._create_about_tab(notebook)
    
    def _create_security_settings(self, notebook):
        """Create security settings tab."""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="🔒 Security")
        
        form = ttk.Frame(tab)
        form.pack(fill=tk.X, padx=20, pady=20)
        
        # Session timeout
        ttk.Label(form, text="Session Timeout (minutes):").grid(row=0, column=0, sticky='w', pady=10)
        self.session_timeout = tk.StringVar(value="30")
        ttk.Entry(form, textvariable=self.session_timeout, width=10).grid(row=0, column=1, padx=10)
        
        # Max login attempts
        ttk.Label(form, text="Max Failed Login Attempts:").grid(row=1, column=0, sticky='w', pady=10)
        self.max_attempts = tk.StringVar(value="5")
        ttk.Entry(form, textvariable=self.max_attempts, width=10).grid(row=1, column=1, padx=10)
        
        # Min password length
        ttk.Label(form, text="Minimum Password Length:").grid(row=2, column=0, sticky='w', pady=10)
        self.min_password = tk.StringVar(value="8")
        ttk.Entry(form, textvariable=self.min_password, width=10).grid(row=2, column=1, padx=10)
        
        # Two-factor auth
        ttk.Label(form, text="Require Two-Factor Auth:").grid(row=3, column=0, sticky='w', pady=10)
        self.require_2fa = tk.BooleanVar(value=False)
        ttk.Checkbutton(form, variable=self.require_2fa).grid(row=3, column=1, sticky='w', padx=10)
        
        # Info
        info_frame = ttk.Labelframe(tab, text="ℹ️ Security Info")
        info_frame.pack(fill=tk.X, padx=20, pady=20)
        
        info_text = """
• Active Security Models: RBAC, MLS, Inference Control, Flow Control, Encryption
• Encryption Algorithm: AES-256
• Password Hashing: bcrypt with salt
• MLS Mode: Bell-LaPadula (No Read Up + No Write Down)
        """
        ttk.Label(info_frame, text=info_text, justify=tk.LEFT).pack(padx=10, pady=10)
    
    def _create_system_settings(self, notebook):
        """Create system settings tab."""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="⚙️ System")
        
        form = ttk.Frame(tab)
        form.pack(fill=tk.X, padx=20, pady=20)
        
        # Maintenance mode
        ttk.Label(form, text="Maintenance Mode:").grid(row=0, column=0, sticky='w', pady=10)
        self.maintenance_mode = tk.BooleanVar(value=False)
        ttk.Checkbutton(form, variable=self.maintenance_mode).grid(row=0, column=1, sticky='w', padx=10)
        
        # Audit logging
        ttk.Label(form, text="Enable Audit Logging:").grid(row=1, column=0, sticky='w', pady=10)
        self.audit_logging = tk.BooleanVar(value=True)
        ttk.Checkbutton(form, variable=self.audit_logging).grid(row=1, column=1, sticky='w', padx=10)
        
        # Database info
        db_frame = ttk.Labelframe(tab, text="📊 Database Info")
        db_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Get database stats
        user_count = self.db.fetch_one("SELECT COUNT(*) as c FROM USERS")['c']
        student_count = self.db.fetch_one("SELECT COUNT(*) as c FROM STUDENT")['c']
        log_count = self.db.fetch_one("SELECT COUNT(*) as c FROM AUDIT_LOG")['c']
        
        stats = f"""
• Total Users: {user_count}
• Total Students: {student_count}
• Audit Log Entries: {log_count}
• Database Path: database/srms.db
        """
        ttk.Label(db_frame, text=stats, justify=tk.LEFT).pack(padx=10, pady=10)
        
        # Actions
        action_frame = ttk.Frame(tab)
        action_frame.pack(fill=tk.X, padx=20, pady=10)
        
        if HAS_TTKBOOTSTRAP:
            ttk.Button(action_frame, text="🧹 Clear Audit Logs", 
                       command=self._clear_audit_logs, bootstyle="warning-outline").pack(side=tk.LEFT, padx=5)
            ttk.Button(action_frame, text="📊 Export Database",
                       command=self._export_database, bootstyle="info-outline").pack(side=tk.LEFT, padx=5)
        else:
            ttk.Button(action_frame, text="Clear Logs", command=self._clear_audit_logs).pack(side=tk.LEFT, padx=5)
            ttk.Button(action_frame, text="Export DB", command=self._export_database).pack(side=tk.LEFT, padx=5)
    
    def _create_about_tab(self, notebook):
        """Create about tab."""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="ℹ️ About")
        
        about_text = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║     🔐 SRMS - Secure Student Records Management System       ║
║                                                              ║
║     Database Security Term Project - Phase 2                 ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║     Version: 2.0.0                                           ║
║     Framework: Python + Tkinter + ttkbootstrap               ║
║     Database: SQLite                                         ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║     Security Features:                                       ║
║     ✅ Role-Based Access Control (RBAC)                      ║
║     ✅ Multilevel Security (Bell-LaPadula)                   ║
║     ✅ Inference Control                                     ║
║     ✅ Flow Control                                          ║
║     ✅ AES-256 Encryption                                    ║
║     ✅ bcrypt Password Hashing                               ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
        """
        
        text_widget = tk.Text(tab, wrap=tk.NONE, font=('Consolas', 10), height=20)
        text_widget.insert('1.0', about_text)
        text_widget.config(state='disabled')
        text_widget.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    def _load_settings(self):
        """Load settings from database."""
        settings = self.db.fetch_all("SELECT * FROM SYSTEM_SETTINGS")
        
        for setting in settings:
            key = setting['setting_key']
            value = setting['setting_value']
            
            if key == 'session_timeout_minutes':
                self.session_timeout.set(value)
            elif key == 'max_login_attempts':
                self.max_attempts.set(value)
            elif key == 'password_min_length':
                self.min_password.set(value)
            elif key == 'require_2fa':
                self.require_2fa.set(value == 'true')
            elif key == 'maintenance_mode':
                self.maintenance_mode.set(value == 'true')
    
    def _save_settings(self):
        """Save settings to database."""
        from tkinter import messagebox
        
        settings = [
            ('session_timeout_minutes', self.session_timeout.get()),
            ('max_login_attempts', self.max_attempts.get()),
            ('password_min_length', self.min_password.get()),
            ('require_2fa', 'true' if self.require_2fa.get() else 'false'),
            ('maintenance_mode', 'true' if self.maintenance_mode.get() else 'false'),
        ]
        
        for key, value in settings:
            self.db.execute("""
                UPDATE SYSTEM_SETTINGS SET setting_value = ?, updated_at = ?
                WHERE setting_key = ?
            """, (value, datetime.now(), key))
        
        self.db.commit()
        messagebox.showinfo("Success", "Settings saved successfully!")
    
    def _clear_audit_logs(self):
        """Clear old audit logs."""
        from tkinter import messagebox
        
        if messagebox.askyesno("Confirm", "Clear all audit logs older than 30 days?"):
            cutoff = (datetime.now() - timedelta(days=30)).isoformat()
            self.db.execute("DELETE FROM AUDIT_LOG WHERE timestamp < ?", (cutoff,))
            self.db.commit()
            messagebox.showinfo("Success", "Old audit logs cleared!")
    
    def _export_database(self):
        """Export database backup."""
        from tkinter import filedialog, messagebox
        import shutil
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".db",
            filetypes=[("SQLite Database", "*.db"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                shutil.copy('database/srms.db', filename)
                messagebox.showinfo("Success", f"Database exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {e}")
