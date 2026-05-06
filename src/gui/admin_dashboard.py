"""
SRMS - Complete Admin Dashboard with All Features
Premium UI with Full Functionality + Advanced Features
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.database.connection import get_database, is_sqlserver
from src.gui.modern_theme import get_theme, show_toast, ColorThemes

# Advanced Features
from src.gui.components import SearchBar
from src.utils import ExportDialog, ShortcutManager
from src.gui.security_dashboard import SecurityDashboard


class AdminDashboard(ttk.Frame):
    """Complete Admin Dashboard with all management features."""
    
    def __init__(self, parent, user, on_logout, theme=None):
        super().__init__(parent)
        self.user = user
        self.on_logout = on_logout
        self.db = get_database()
        self.theme = theme if theme else get_theme()
        
        # Data storage for search/export
        self.current_data = []
        self.current_columns = []
        self.current_view = 'overview'
        
        # Setup keyboard shortcuts
        self._setup_shortcuts()
        
        self._create_layout()
    
    def _create_layout(self):
        """Create main dashboard layout."""
        # Header bar
        self._create_header()
        
        # Main content area
        content = ttk.Frame(self)
        content.pack(fill=tk.BOTH, expand=True)
        
        # Left sidebar
        self._create_sidebar(content)
        
        # Main panel
        self.main_panel = ttk.Frame(content)
        self.main_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Show overview by default
        self._show_overview()
    
    def _create_header(self):
        """Create modern header bar."""
        header = tk.Frame(self, bg=self.theme['bg_secondary'], height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        # Left side - Title
        left = tk.Frame(header, bg=self.theme['bg_secondary'])
        left.pack(side=tk.LEFT, fill=tk.Y, padx=20)
        
        tk.Label(left, text="🔐", font=('Segoe UI', 20),
                bg=self.theme['bg_secondary'], fg=self.theme['accent']).pack(side=tk.LEFT)
        tk.Label(left, text=" Admin Dashboard", font=('Segoe UI', 16, 'bold'),
                bg=self.theme['bg_secondary'], fg=self.theme['text_primary']).pack(side=tk.LEFT)
        
        # Right side - User info
        right = tk.Frame(header, bg=self.theme['bg_secondary'])
        right.pack(side=tk.RIGHT, fill=tk.Y, padx=20)
        
        # Connection status
        conn_status = "🟢 SQL Server" if is_sqlserver() else "🟡 SQLite"
        tk.Label(right, text=conn_status, font=('Segoe UI', 10),
                bg=self.theme['bg_secondary'], fg=self.theme['success']).pack(side=tk.LEFT, padx=15)
        
        # User info
        tk.Label(right, text=f"👤 {self.user.get('username', 'admin')}",
                font=('Segoe UI', 11),
                bg=self.theme['bg_secondary'], fg=self.theme['text_primary']).pack(side=tk.LEFT, padx=5)
        
        tk.Label(right, text=f"[Level {self.user.get('clearance_level', 4)}]",
                font=('Segoe UI', 10),
                bg=self.theme['bg_secondary'], fg=self.theme['text_secondary']).pack(side=tk.LEFT, padx=5)
        
        # Logout button
        logout_btn = tk.Button(right, text="🚪 Logout", font=('Segoe UI', 10),
                               bg=self.theme['error'], fg='#ffffff',
                               relief='flat', cursor='hand2', padx=15,
                               command=self.on_logout)
        logout_btn.pack(side=tk.LEFT, padx=15, pady=15)
    
    def _create_sidebar(self, parent):
        """Create navigation sidebar."""
        sidebar = tk.Frame(parent, bg=self.theme['bg_secondary'], width=220)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(10, 0), pady=10)
        sidebar.pack_propagate(False)
        
        # Navigation title
        tk.Label(sidebar, text="📋 Navigation", font=('Segoe UI', 12, 'bold'),
                bg=self.theme['bg_secondary'], fg=self.theme['text_primary']).pack(pady=15)
        
        # Navigation buttons
        nav_items = [
            ("📊", "Overview", self._show_overview),
            ("👥", "Users", self._show_users),
            ("📝", "Role Requests", self._show_role_requests),
            ("🎓", "Students", self._show_students),
            ("👨‍🏫", "Instructors", self._show_instructors),
            ("📚", "Courses", self._show_courses),
            ("📈", "Grades", self._show_grades),
            ("📅", "Attendance", self._show_attendance),
            ("🔒", "Audit Log", self._show_audit_log),
            ("🛡️", "Security", self._show_security_dashboard),
            ("💾", "SQL Viewer", self._show_sql_viewer),
            ("🔧", "Settings", self._show_settings),
        ]
        
        for icon, text, command in nav_items:
            btn_frame = tk.Frame(sidebar, bg=self.theme['bg_secondary'])
            btn_frame.pack(fill=tk.X, padx=10, pady=3)
            
            btn = tk.Button(btn_frame, text=f"{icon}  {text}",
                           font=('Segoe UI', 11), anchor='w',
                           bg=self.theme['bg_secondary'],
                           fg=self.theme['text_secondary'],
                           activebackground=self.theme['accent'],
                           activeforeground='#ffffff',
                           relief='flat', cursor='hand2',
                           command=command)
            btn.pack(fill=tk.X, ipady=8)
            
            # Hover effect
            btn.bind('<Enter>', lambda e, b=btn: b.config(bg=self.theme['bg_card']))
            btn.bind('<Leave>', lambda e, b=btn: b.config(bg=self.theme['bg_secondary']))
    
    def _clear_panel(self):
        """Clear main panel."""
        for widget in self.main_panel.winfo_children():
            widget.destroy()
    
    def _create_card(self, parent, title=""):
        """Create a modern card widget."""
        card = tk.Frame(parent, bg=self.theme['bg_card'],
                       highlightthickness=1,
                       highlightbackground=self.theme['border'])
        
        if title:
            tk.Label(card, text=title, font=('Segoe UI', 14, 'bold'),
                    bg=self.theme['bg_card'], fg=self.theme['text_primary']).pack(
                        anchor='w', padx=15, pady=(15, 10))
        
        return card
    
    def _setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        try:
            root = self.winfo_toplevel()
            self.shortcuts = ShortcutManager(self, root)
            
            # Register shortcuts
            self.shortcuts.register_refresh(self._refresh_current_view)
            self.shortcuts.register_export(self._export_current_data)
            self.shortcuts.register_logout(self.on_logout)
            self.shortcuts.register_help()  # F1 for help
        except Exception as e:
            print(f"Shortcuts setup error: {e}")
    
    def _refresh_current_view(self):
        """Refresh current view"""
        if self.current_view == 'users':
            self._show_users()
        elif self.current_view == 'students':
            self._show_students()
        elif self.current_view == 'grades':
            self._show_grades()
        elif self.current_view == 'requests':
            self._show_role_requests()
        else:
            self._show_overview()
        
        show_toast("Data refreshed!", 'success')
    
    def _export_current_data(self):
        """Export current view data"""
        if not self.current_data or not self.current_columns:
            messagebox.showinfo("Export", "No data to export in current view")
            return
        
        # Admin can export everything
        classified = False
        
        ExportDialog.show(
            self,
            data=self.current_data,
            columns=self.current_columns,
            default_name=f"{self.current_view}_export",
            classified=classified
        )
    
    def _show_overview(self):
        """Show dashboard overview."""
        self._clear_panel()
        
        # Title
        tk.Label(self.main_panel, text="📊 System Overview",
                font=('Segoe UI', 18, 'bold'),
                bg=self.theme['bg_primary'], fg=self.theme['text_primary']).pack(anchor='w', pady=(0, 20))
        
        # Stats cards row
        stats_frame = tk.Frame(self.main_panel, bg=self.theme['bg_primary'])
        stats_frame.pack(fill=tk.X, pady=10)
        
        stats = self._get_stats()
        colors = [self.theme['accent'], '#7209b7', '#f72585', '#4cc9f0', '#06d6a0']
        
        for i, (label, value) in enumerate(stats.items()):
            card = tk.Frame(stats_frame, bg=self.theme['bg_card'],
                           highlightthickness=2, highlightbackground=colors[i % len(colors)])
            card.pack(side=tk.LEFT, padx=10, pady=5, ipadx=20, ipady=15)
            
            tk.Label(card, text=str(value), font=('Segoe UI', 28, 'bold'),
                    bg=self.theme['bg_card'], fg=colors[i % len(colors)]).pack()
            tk.Label(card, text=label, font=('Segoe UI', 11),
                    bg=self.theme['bg_card'], fg=self.theme['text_secondary']).pack()
        
        # Security models card
        security_card = self._create_card(self.main_panel, "🛡️ Security Models Active")
        security_card.pack(fill=tk.X, pady=20)
        
        models = [
            ("✅ RBAC", "5 roles with granular permissions"),
            ("✅ MLS", "Bell-LaPadula (No Read Up)"),
            ("✅ Encryption", "AES-256 for sensitive data"),
            ("✅ Inference Control", "Min 3 records for statistics"),
            ("✅ Flow Control", "Prevent data downflow"),
        ]
        
        for model, desc in models:
            row = tk.Frame(security_card, bg=self.theme['bg_card'])
            row.pack(fill=tk.X, padx=15, pady=3)
            tk.Label(row, text=model, font=('Segoe UI', 11, 'bold'), width=18, anchor='w',
                    bg=self.theme['bg_card'], fg=self.theme['success']).pack(side=tk.LEFT)
            tk.Label(row, text=desc, font=('Segoe UI', 10),
                    bg=self.theme['bg_card'], fg=self.theme['text_secondary']).pack(side=tk.LEFT)
        
        tk.Frame(security_card, height=15, bg=self.theme['bg_card']).pack()
        
        # Connection info card
        conn_card = self._create_card(self.main_panel, "💾 Database Connection")
        conn_card.pack(fill=tk.X, pady=10)
        
        conn_info = [
            ("Type", "Microsoft SQL Server" if is_sqlserver() else "SQLite"),
            ("Server", "localhost:1433" if is_sqlserver() else "Local File"),
            ("Database", "SRMS_SecureDB" if is_sqlserver() else "srms.db"),
            ("Status", "🟢 Connected"),
        ]
        
        for label, value in conn_info:
            row = tk.Frame(conn_card, bg=self.theme['bg_card'])
            row.pack(fill=tk.X, padx=15, pady=3)
            tk.Label(row, text=f"{label}:", font=('Segoe UI', 11, 'bold'), width=12, anchor='w',
                    bg=self.theme['bg_card'], fg=self.theme['text_secondary']).pack(side=tk.LEFT)
            tk.Label(row, text=value, font=('Segoe UI', 11),
                    bg=self.theme['bg_card'], fg=self.theme['text_primary']).pack(side=tk.LEFT)
        
        tk.Frame(conn_card, height=15, bg=self.theme['bg_card']).pack()
    
    def _get_stats(self):
        """Get system statistics."""
        try:
            return {
                'Users': self.db.fetch_one("SELECT COUNT(*) as c FROM USERS")['c'],
                'Students': self.db.fetch_one("SELECT COUNT(*) as c FROM STUDENT")['c'],
                'Instructors': self.db.fetch_one("SELECT COUNT(*) as c FROM INSTRUCTOR")['c'],
                'Courses': self.db.fetch_one("SELECT COUNT(*) as c FROM COURSE")['c'],
                'Grades': self.db.fetch_one("SELECT COUNT(*) as c FROM GRADES")['c'],
            }
        except:
            return {'Users': 0, 'Students': 0, 'Instructors': 0, 'Courses': 0, 'Grades': 0}
    
    def _show_users(self):
        """Show user management."""
        self._clear_panel()
        self.current_view = 'users'
        
        # Title
        header = tk.Frame(self.main_panel, bg=self.theme['bg_primary'])
        header.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(header, text="👥 User Management",
                font=('Segoe UI', 18, 'bold'),
                bg=self.theme['bg_primary'], fg=self.theme['text_primary']).pack(side=tk.LEFT)
        
        # Search bar
        self.users_search = SearchBar(header, self._filter_users, placeholder="Search users...")
        self.users_search.pack(side=tk.LEFT, padx=20, fill=tk.X, expand=True)
        
        # Action buttons
        btn_frame = tk.Frame(self.main_panel, bg=self.theme['bg_primary'])
        btn_frame.pack(fill=tk.X, pady=10)
        
        tk.Button(btn_frame, text="➕ Add User", font=('Segoe UI', 10),
                 bg=self.theme['accent'], fg='#fff', relief='flat',
                 command=self._add_user_dialog).pack(side=tk.LEFT, padx=5, ipadx=15, ipady=5)
        
        tk.Button(btn_frame, text="📊 Export", font=('Segoe UI', 10),
                 bg=self.theme['success'], fg='#fff', relief='flat',
                 command=self._export_current_data).pack(side=tk.LEFT, padx=5, ipadx=15, ipady=5)
        
        tk.Button(btn_frame, text="🔄 Refresh", font=('Segoe UI', 10),
                 bg=self.theme['bg_card'], fg=self.theme['text_primary'], relief='flat',
                 command=self._show_users).pack(side=tk.LEFT, padx=5, ipadx=15, ipady=5)
        
        # Keyboard hint
        tk.Label(btn_frame, text="💡 Tip: Ctrl+F to search, Ctrl+E to export, Ctrl+R to refresh",
                font=('Segoe UI', 9), bg=self.theme['bg_primary'], 
                fg=self.theme['text_secondary']).pack(side=tk.RIGHT, padx=10)
        
        # Load and display data
        self._load_users_data()
    
    def _load_users_data(self):
        """Load users data and update table"""
        self.current_columns = ['ID', 'Username', 'Role', 'Clearance', 'Active', 'Last Login']
        self.current_data = self._get_users_data()
        self.all_users_data = self.current_data.copy()  # Keep original
        
        # Table
        self._create_data_table(self.current_columns, self.current_data)
    
    def _filter_users(self, search_text):
        """Filter users based on search text"""
        if not search_text:
            self.current_data = self.all_users_data.copy()
        else:
            search_lower = search_text.lower()
            self.current_data = [
                row for row in self.all_users_data
                if any(search_lower in str(val).lower() for val in row)
            ]
        
        # Update table
        self._create_data_table(self.current_columns, self.current_data)
    
    def _get_users_data(self):
        """Get users data from database."""
        try:
            if is_sqlserver():
                users = self.db.fetch_all(
                    "SELECT UserID, Username, Role, ClearanceLevel, IsActive, LastLoginDate FROM USERS"
                )
                return [(u['UserID'], u['Username'], u['Role'], u['ClearanceLevel'],
                        "✓" if u.get('IsActive', 1) else "✗",
                        str(u.get('LastLoginDate', ''))[:10] if u.get('LastLoginDate') else 'Never')
                       for u in users]
        except:
            pass
        return []
    
    def _add_user_dialog(self):
        """Show add user dialog."""
        dialog = tk.Toplevel(self)
        dialog.title("Add New User")
        dialog.geometry("500x650")
        dialog.configure(bg=self.theme['bg_primary'])
        
        # Center dialog
        dialog.update_idletasks()
        x = self.winfo_screenwidth() // 2 - 250
        y = self.winfo_screenheight() // 2 - 325
        dialog.geometry(f"+{x}+{y}")
        
        # Header
        header = tk.Frame(dialog, bg=self.theme['bg_secondary'], height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text="👤 Add User", font=('Segoe UI', 20, 'bold'),
                bg=self.theme['bg_secondary'], fg=self.theme['accent']).pack(side=tk.LEFT, padx=20)
        
        # Form Container
        form = tk.Frame(dialog, bg=self.theme['bg_primary'], padx=40, pady=30)
        form.pack(fill=tk.BOTH, expand=True)
        
        # Username
        tk.Label(form, text="USERNAME", font=('Segoe UI', 10, 'bold'),
                bg=self.theme['bg_primary'], fg=self.theme['text_secondary']).pack(anchor='w')
        username_var = tk.StringVar()
        entry_user = tk.Entry(form, textvariable=username_var, font=('Segoe UI', 12),
                             bg=self.theme['bg_card'], fg=self.theme['text_primary'],
                             relief='flat', insertbackground=self.theme['accent'])
        entry_user.pack(fill=tk.X, pady=(5, 20), ipady=8)
        
        # Password
        tk.Label(form, text="PASSWORD", font=('Segoe UI', 10, 'bold'),
                bg=self.theme['bg_primary'], fg=self.theme['text_secondary']).pack(anchor='w')
        password_var = tk.StringVar()
        entry_pass = tk.Entry(form, textvariable=password_var, font=('Segoe UI', 12), show='●',
                             bg=self.theme['bg_card'], fg=self.theme['text_primary'],
                             relief='flat', insertbackground=self.theme['accent'])
        entry_pass.pack(fill=tk.X, pady=(5, 20), ipady=8)
        
        # Role
        tk.Label(form, text="ROLE", font=('Segoe UI', 10, 'bold'),
                bg=self.theme['bg_primary'], fg=self.theme['text_secondary']).pack(anchor='w')
        role_var = tk.StringVar(value='Student')
        role_combo = ttk.Combobox(form, textvariable=role_var, font=('Segoe UI', 11),
                                   values=['Admin', 'Instructor', 'TA', 'Student', 'Guest'])
        role_combo.pack(fill=tk.X, pady=(5, 20), ipady=5)
        
        # Security Badge
        tk.Label(form, text="🛡️ Security Clearance will be assigned automatically",
                font=('Segoe UI', 9), bg=self.theme['bg_primary'], fg=self.theme['success']).pack(pady=10)
        
        def create():
            import hashlib, os as os_mod
            username = username_var.get().strip()
            password = password_var.get()
            role = role_var.get()
            
            if not username or not password:
                messagebox.showerror("Error", "Username and password required")
                return
            
            clearance = {'Admin': 4, 'Instructor': 3, 'TA': 2, 'Student': 1, 'Guest': 0}.get(role, 0)
            
            try:
                salt = os_mod.urandom(16)
                password_hash = hashlib.sha256((password + salt.hex()).encode('utf-8')).digest()
                
                if is_sqlserver():
                    # Use Stored Procedure sp_AddUser
                    self.db.execute(
                        "EXEC usp_AddUser @Username=%s, @PasswordHash=%s, @PasswordSalt=%s, @Role=%s, @ClearanceLevel=%s, @ExecutorRole='Admin'",
                        (username, password_hash, salt, role, clearance)
                    )
                    self.db.commit()
                    show_toast(f"User '{username}' created successfully!", 'success')
                    dialog.destroy()
                    self._show_users()
            except Exception as e:
                messagebox.showerror("Database Error", f"Failed to create user:\n{e}")
        
        # Buttons
        btn_frame = tk.Frame(form, bg=self.theme['bg_primary'])
        btn_frame.pack(fill=tk.X, pady=20)
        
        tk.Button(btn_frame, text="Cancel", font=('Segoe UI', 11),
                 bg=self.theme['bg_card'], fg=self.theme['text_secondary'], relief='flat',
                 command=dialog.destroy).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 10), ipady=10)
        
        tk.Button(btn_frame, text="Create User", font=('Segoe UI', 11, 'bold'),
                 bg=self.theme['accent'], fg='#fff', relief='flat',
                 command=create).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(10, 0), ipady=10)
    
    def _show_role_requests(self):
        """Show role requests (Part B)."""
        self._clear_panel()
        
        tk.Label(self.main_panel, text="📝 Role Upgrade Requests (Part B)",
                font=('Segoe UI', 18, 'bold'),
                bg=self.theme['bg_primary'], fg=self.theme['text_primary']).pack(anchor='w', pady=(0, 15))
        
        # Pending requests
        pending_card = self._create_card(self.main_panel, "⏳ Pending Requests")
        pending_card.pack(fill=tk.X, pady=10)
        
        try:
            if is_sqlserver():
                requests = self.db.fetch_all(
                    "SELECT RequestID, Username, CurrentRole, RequestedRole, Reason, DateSubmitted "
                    "FROM ROLE_REQUESTS WHERE Status = %s ORDER BY DateSubmitted",
                    ('Pending',)
                )
                
                # Create request cards with details
                for r in requests:
                    request_frame = tk.Frame(pending_card, bg=self.theme['bg_secondary'],
                                           highlightthickness=1, highlightbackground=self.theme['accent'])
                    request_frame.pack(fill=tk.X, padx=15, pady=8)
                    
                    # Header row
                    header = tk.Frame(request_frame, bg=self.theme['bg_secondary'])
                    header.pack(fill=tk.X, padx=10, pady=(10, 5))
                    
                    tk.Label(header, text=f"🎫 Request #{r['RequestID']}", 
                            font=('Segoe UI', 11, 'bold'),
                            bg=self.theme['bg_secondary'], fg=self.theme['accent']).pack(side=tk.LEFT)
                    tk.Label(header, text=f"📅 {str(r['DateSubmitted'])[:10]}", 
                            font=('Segoe UI', 9),
                            bg=self.theme['bg_secondary'], fg=self.theme['text_secondary']).pack(side=tk.RIGHT)
                    
                    # Details row
                    details = tk.Frame(request_frame, bg=self.theme['bg_secondary'])
                    details.pack(fill=tk.X, padx=10, pady=5)
                    
                    tk.Label(details, text=f"👤 {r['Username']}", width=15, anchor='w',
                            font=('Segoe UI', 10),
                            bg=self.theme['bg_secondary'], fg=self.theme['text_primary']).pack(side=tk.LEFT)
                    tk.Label(details, text=f"{r['CurrentRole']} → {r['RequestedRole']}", 
                            font=('Segoe UI', 10, 'bold'),
                            bg=self.theme['bg_secondary'], fg=self.theme['success']).pack(side=tk.LEFT, padx=10)
                    
                    # Reason
                    reason_frame = tk.Frame(request_frame, bg=self.theme['bg_secondary'])
                    reason_frame.pack(fill=tk.X, padx=10, pady=5)
                    
                    tk.Label(reason_frame, text="📋 Reason:", 
                            font=('Segoe UI', 9, 'bold'),
                            bg=self.theme['bg_secondary'], fg=self.theme['text_secondary']).pack(anchor='w')
                    tk.Label(reason_frame, text=r.get('Reason', 'No reason provided')[:100], 
                            font=('Segoe UI', 9), wraplength=500,
                            bg=self.theme['bg_secondary'], fg=self.theme['text_primary']).pack(anchor='w')
                    
                    # Admin Comments Section
                    comments_frame = tk.Frame(request_frame, bg=self.theme['bg_secondary'])
                    comments_frame.pack(fill=tk.X, padx=10, pady=5)
                    
                    tk.Label(comments_frame, text="💬 Admin Comments:", 
                            font=('Segoe UI', 9, 'bold'),
                            bg=self.theme['bg_secondary'], fg=self.theme['text_secondary']).pack(anchor='w')
                    
                    comment_var = tk.StringVar()
                    comment_entry = tk.Entry(comments_frame, textvariable=comment_var,
                                            font=('Segoe UI', 10), width=50)
                    comment_entry.pack(fill=tk.X, pady=5)
                    comment_entry.insert(0, "Enter your comments here...")
                    comment_entry.bind('<FocusIn>', lambda e, ent=comment_entry: ent.delete(0, tk.END) if ent.get() == "Enter your comments here..." else None)
                    
                    # Store reference for later
                    request_frame.comment_var = comment_var
                    
                    # Action buttons
                    btn_frame = tk.Frame(request_frame, bg=self.theme['bg_secondary'])
                    btn_frame.pack(fill=tk.X, padx=10, pady=(5, 10))
                    
                    tk.Button(btn_frame, text="✅ Approve", font=('Segoe UI', 10, 'bold'),
                             bg=self.theme['success'], fg='#fff', relief='flat',
                             command=lambda rid=r['RequestID'], cv=comment_var: self._process_request_with_comments(rid, 'Approved', cv.get())).pack(
                                 side=tk.LEFT, padx=5, ipadx=20, ipady=5)
                    tk.Button(btn_frame, text="❌ Deny", font=('Segoe UI', 10, 'bold'),
                             bg=self.theme['error'], fg='#fff', relief='flat',
                             command=lambda rid=r['RequestID'], cv=comment_var: self._process_request_with_comments(rid, 'Denied', cv.get())).pack(
                                 side=tk.LEFT, padx=5, ipadx=20, ipady=5)
                
                if not requests:
                    tk.Label(pending_card, text="✅ No pending requests - All caught up!", 
                            font=('Segoe UI', 12),
                            bg=self.theme['bg_card'], fg=self.theme['success']).pack(pady=20)
        except Exception as e:
            tk.Label(pending_card, text=f"Error: {e}",
                    bg=self.theme['bg_card'], fg=self.theme['error']).pack(pady=10)
        
        tk.Frame(pending_card, height=15, bg=self.theme['bg_card']).pack()
        
        # History section
        history_card = self._create_card(self.main_panel, "📜 Request History")
        history_card.pack(fill=tk.X, pady=10)
        
        try:
            if is_sqlserver():
                history = self.db.fetch_all(
                    "SELECT TOP 10 RequestID, Username, CurrentRole, RequestedRole, Status, "
                    "AdminComments, DateSubmitted, DateProcessed "
                    "FROM ROLE_REQUESTS WHERE Status != 'Pending' ORDER BY DateProcessed DESC"
                )
                
                if history:
                    for h in history:
                        row = tk.Frame(history_card, bg=self.theme['bg_card'])
                        row.pack(fill=tk.X, padx=15, pady=3)
                        
                        status_color = self.theme['success'] if h['Status'] == 'Approved' else self.theme['error']
                        status_icon = "✅" if h['Status'] == 'Approved' else "❌"
                        
                        tk.Label(row, text=f"#{h['RequestID']}", width=5,
                                bg=self.theme['bg_card'], fg=self.theme['text_secondary']).pack(side=tk.LEFT)
                        tk.Label(row, text=h['Username'], width=12,
                                bg=self.theme['bg_card'], fg=self.theme['text_primary']).pack(side=tk.LEFT)
                        tk.Label(row, text=f"{h['CurrentRole']} → {h['RequestedRole']}", width=18,
                                bg=self.theme['bg_card'], fg=self.theme['accent']).pack(side=tk.LEFT)
                        tk.Label(row, text=f"{status_icon} {h['Status']}", width=10,
                                bg=self.theme['bg_card'], fg=status_color).pack(side=tk.LEFT)
                        
                        # Show admin comments if any
                        if h.get('AdminComments'):
                            tk.Label(row, text=f"💬 {h['AdminComments'][:30]}...",
                                    bg=self.theme['bg_card'], fg=self.theme['text_secondary']).pack(side=tk.LEFT, padx=10)
                else:
                    tk.Label(history_card, text="No processed requests yet",
                            bg=self.theme['bg_card'], fg=self.theme['text_secondary']).pack(pady=10)
        except:
            pass
        
        tk.Frame(history_card, height=15, bg=self.theme['bg_card']).pack()
    
    def _process_request_with_comments(self, request_id, status, comments):
        """Process role request with admin comments."""
        # Clean up placeholder text
        if comments == "Enter your comments here...":
            comments = ""
        
        try:
            if is_sqlserver():
                # Update with comments
                self.db.execute(
                    "UPDATE ROLE_REQUESTS SET AdminComments = %s WHERE RequestID = %s",
                    (comments, request_id)
                )
                self.db.commit()
                
                # Process the request
                self._process_request(request_id, status)
        except Exception as e:
            show_toast(f"Error: {e}", 'error')
    
    def _process_request(self, request_id, status):
        """Process role request."""
        try:
            if is_sqlserver():
                # Use Stored Procedure sp_ProcessRoleRequest
                self.db.execute(
                    "EXEC usp_ProcessRoleRequest @RequestID=%s, @Status=%s, @AdminID=%s, @AdminUsername=%s",
                    (request_id, status, self.user.get('user_id'), self.user.get('username'))
                )
                self.db.commit()
                show_toast(f"Request {status}!", 'success')
                self._show_role_requests()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def _show_students(self):
        """Show students."""
        self._clear_panel()
        self.current_view = 'students'
        
        # Header with search
        header = tk.Frame(self.main_panel, bg=self.theme['bg_primary'])
        header.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(header, text="🎓 Students",
                font=('Segoe UI', 18, 'bold'),
                bg=self.theme['bg_primary'], fg=self.theme['text_primary']).pack(side=tk.LEFT)
        
        # Search bar
        self.students_search = SearchBar(header, self._filter_students, placeholder="Search students...")
        self.students_search.pack(side=tk.LEFT, padx=20, fill=tk.X, expand=True)
        
        # Action buttons
        btn_frame = tk.Frame(self.main_panel, bg=self.theme['bg_primary'])
        btn_frame.pack(fill=tk.X, pady=10)
        
        tk.Button(btn_frame, text="📊 Export", font=('Segoe UI', 10),
                 bg=self.theme['success'], fg='#fff', relief='flat',
                 command=self._export_current_data).pack(side=tk.LEFT, padx=5, ipadx=15, ipady=5)
        
        tk.Button(btn_frame, text="🔄 Refresh", font=('Segoe UI', 10),
                 bg=self.theme['bg_card'], fg=self.theme['text_primary'], relief='flat',
                 command=self._show_students).pack(side=tk.LEFT, padx=5, ipadx=15, ipady=5)
        
        # Load data
        self._load_students_data()
    
    def _load_students_data(self):
        """Load students data"""
        self.current_columns = ['ID', 'Name', 'Email', 'Department', 'Status']
        self.current_data = []
        
        try:
            if is_sqlserver():
                students = self.db.fetch_all("SELECT StudentID, FullName, Email, Department, Status FROM STUDENT")
                self.current_data = [(s['StudentID'], s['FullName'], s['Email'], s.get('Department', ''), s.get('Status', 'Active'))
                       for s in students]
        except:
            pass
        
        self.all_students_data = self.current_data.copy()
        self._create_data_table(self.current_columns, self.current_data)
    
    def _filter_students(self, search_text):
        """Filter students based on search text"""
        if not search_text:
            self.current_data = self.all_students_data.copy()
        else:
            search_lower = search_text.lower()
            self.current_data = [
                row for row in self.all_students_data
                if any(search_lower in str(val).lower() for val in row)
            ]
        self._create_data_table(self.current_columns, self.current_data)
    
    def _show_instructors(self):
        """Show instructors."""
        self._clear_panel()
        tk.Label(self.main_panel, text="👨‍🏫 Instructors",
                font=('Segoe UI', 18, 'bold'),
                bg=self.theme['bg_primary'], fg=self.theme['text_primary']).pack(anchor='w', pady=(0, 15))
        
        data = []
        try:
            if is_sqlserver():
                instructors = self.db.fetch_all("SELECT InstructorID, FullName, Email, Department, Title FROM INSTRUCTOR")
                data = [(i['InstructorID'], i['FullName'], i['Email'], i.get('Department', ''), i.get('Title', ''))
                       for i in instructors]
        except:
            pass
        
        self._create_data_table(['ID', 'Name', 'Email', 'Department', 'Title'], data)
    
    def _show_courses(self):
        """Show courses."""
        self._clear_panel()
        tk.Label(self.main_panel, text="📚 Courses",
                font=('Segoe UI', 18, 'bold'),
                bg=self.theme['bg_primary'], fg=self.theme['text_primary']).pack(anchor='w', pady=(0, 15))
        
        data = []
        try:
            if is_sqlserver():
                courses = self.db.fetch_all("SELECT CourseID, CourseCode, CourseName, Credits, Department FROM COURSE")
                data = [(c['CourseID'], c['CourseCode'], c['CourseName'], c.get('Credits', 3), c.get('Department', ''))
                       for c in courses]
        except:
            pass
        
        self._create_data_table(['ID', 'Code', 'Name', 'Credits', 'Department'], data)
    
    def _show_grades(self):
        """Show grades."""
        self._clear_panel()
        self.current_view = 'grades'
        
        # Header with search
        header = tk.Frame(self.main_panel, bg=self.theme['bg_primary'])
        header.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(header, text="📈 Grades (Secret Classification)",
                font=('Segoe UI', 18, 'bold'),
                bg=self.theme['bg_primary'], fg=self.theme['text_primary']).pack(side=tk.LEFT)
        
        # Search bar
        self.grades_search = SearchBar(header, self._filter_grades, placeholder="Search grades...")
        self.grades_search.pack(side=tk.LEFT, padx=20, fill=tk.X, expand=True)
        
        # Action buttons
        btn_frame = tk.Frame(self.main_panel, bg=self.theme['bg_primary'])
        btn_frame.pack(fill=tk.X, pady=10)
        
        tk.Button(btn_frame, text="📊 Export", font=('Segoe UI', 10),
                 bg=self.theme['success'], fg='#fff', relief='flat',
                 command=self._export_current_data).pack(side=tk.LEFT, padx=5, ipadx=15, ipady=5)
        
        tk.Button(btn_frame, text="🔄 Refresh", font=('Segoe UI', 10),
                 bg=self.theme['bg_card'], fg=self.theme['text_primary'], relief='flat',
                 command=self._show_grades).pack(side=tk.LEFT, padx=5, ipadx=15, ipady=5)
        
        # Load data
        self._load_grades_data()
    
    def _load_grades_data(self):
        """Load grades data"""
        self.current_columns = ['ID', 'Student', 'Course', 'Grade', 'Letter', 'Published']
        self.current_data = []
        
        try:
            if is_sqlserver():
                grades = self.db.fetch_all("""
                    SELECT g.GradeID, s.FullName, c.CourseCode, g.GradeValue_Display, g.GradeLetter, g.IsPublished
                    FROM GRADES g
                    JOIN STUDENT s ON g.StudentID = s.StudentID
                    JOIN COURSE c ON g.CourseID = c.CourseID
                """)
                self.current_data = [(g['GradeID'], g['FullName'], g['CourseCode'],
                        g.get('GradeValue_Display', ''), g.get('GradeLetter', ''),
                        "✓" if g.get('IsPublished', 0) else "✗")
                       for g in grades]
        except:
            pass
        
        self.all_grades_data = self.current_data.copy()
        self._create_data_table(self.current_columns, self.current_data)
    
    def _filter_grades(self, search_text):
        """Filter grades based on search text"""
        if not search_text:
            self.current_data = self.all_grades_data.copy()
        else:
            search_lower = search_text.lower()
            self.current_data = [
                row for row in self.all_grades_data
                if any(search_lower in str(val).lower() for val in row)
            ]
        self._create_data_table(self.current_columns, self.current_data)
    
    def _show_attendance(self):
        """Show attendance."""
        self._clear_panel()
        tk.Label(self.main_panel, text="📅 Attendance Records",
                font=('Segoe UI', 18, 'bold'),
                bg=self.theme['bg_primary'], fg=self.theme['text_primary']).pack(anchor='w', pady=(0, 15))
        
        data = []
        try:
            if is_sqlserver():
                attendance = self.db.fetch_all("""
                    SELECT a.AttendanceID, s.FullName, c.CourseCode, a.AttendanceDate, a.StatusText
                    FROM ATTENDANCE a
                    JOIN STUDENT s ON a.StudentID = s.StudentID
                    JOIN COURSE c ON a.CourseID = c.CourseID
                    ORDER BY a.AttendanceDate DESC
                """)
                data = [(a['AttendanceID'], a['FullName'], a['CourseCode'],
                        str(a.get('AttendanceDate', ''))[:10], a.get('StatusText', ''))
                       for a in attendance]
        except:
            pass
        
        self._create_data_table(['ID', 'Student', 'Course', 'Date', 'Status'], data)
    
    def _show_audit_log(self):
        """Show audit log."""
        self._clear_panel()
        self.current_view = 'audit'
        
        # Header with search
        header = tk.Frame(self.main_panel, bg=self.theme['bg_primary'])
        header.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(header, text="🔒 Security Audit Log",
                font=('Segoe UI', 18, 'bold'),
                bg=self.theme['bg_primary'], fg=self.theme['text_primary']).pack(side=tk.LEFT)
        
        # Search bar
        self.audit_search = SearchBar(header, self._filter_audit, placeholder="Search audit log...")
        self.audit_search.pack(side=tk.LEFT, padx=20, fill=tk.X, expand=True)
        
        # Action buttons
        btn_frame = tk.Frame(self.main_panel, bg=self.theme['bg_primary'])
        btn_frame.pack(fill=tk.X, pady=10)
        
        tk.Button(btn_frame, text="📊 Export", font=('Segoe UI', 10),
                 bg=self.theme['success'], fg='#fff', relief='flat',
                 command=self._export_current_data).pack(side=tk.LEFT, padx=5, ipadx=15, ipady=5)
        
        tk.Button(btn_frame, text="🔄 Refresh", font=('Segoe UI', 10),
                 bg=self.theme['bg_card'], fg=self.theme['text_primary'], relief='flat',
                 command=self._show_audit_log).pack(side=tk.LEFT, padx=5, ipadx=15, ipady=5)
        
        # Load data
        self._load_audit_data()
    
    def _load_audit_data(self):
        """Load audit log data"""
        self.current_columns = ['ID', 'Action', 'User', 'Role', 'Granted', 'Time']
        self.current_data = []
        
        try:
            if is_sqlserver():
                logs = self.db.fetch_all("""
                    SELECT LogID, ActionType, Username, UserRole, AccessGranted, ActionDate
                    FROM AUDIT_LOG ORDER BY ActionDate DESC
                """)
                self.current_data = [(l['LogID'], l.get('ActionType', ''), l.get('Username', ''),
                        l.get('UserRole', ''), "✓" if l.get('AccessGranted', 0) else "✗",
                        str(l.get('ActionDate', ''))[:19])
                       for l in logs[:100]]  # Show more entries
        except:
            pass
        
        self.all_audit_data = self.current_data.copy()
        self._create_data_table(self.current_columns, self.current_data)
    
    def _filter_audit(self, search_text):
        """Filter audit log based on search text"""
        if not search_text:
            self.current_data = self.all_audit_data.copy()
        else:
            search_lower = search_text.lower()
            self.current_data = [
                row for row in self.all_audit_data
                if any(search_lower in str(val).lower() for val in row)
            ]
        self._create_data_table(self.current_columns, self.current_data)
    
    def _show_sql_viewer(self):
        """Show SQL query viewer - execute queries and see results."""
        self._clear_panel()
        
        tk.Label(self.main_panel, text="💾 SQL Query Viewer (View Server Data)",
                font=('Segoe UI', 18, 'bold'),
                bg=self.theme['bg_primary'], fg=self.theme['text_primary']).pack(anchor='w', pady=(0, 15))
        
        # Connection info
        info_card = self._create_card(self.main_panel, "📡 Connection Status")
        info_card.pack(fill=tk.X, pady=10)
        
        if is_sqlserver():
            tk.Label(info_card, text="🟢 Connected to: localhost:1433 / SRMS_SecureDB",
                    font=('Segoe UI', 11), bg=self.theme['bg_card'],
                    fg=self.theme['success']).pack(anchor='w', padx=15, pady=5)
        else:
            tk.Label(info_card, text="🟡 Using SQLite (local)",
                    font=('Segoe UI', 11), bg=self.theme['bg_card'],
                    fg=self.theme['warning']).pack(anchor='w', padx=15, pady=5)
        
        tk.Frame(info_card, height=10, bg=self.theme['bg_card']).pack()
        
        # Query input
        query_card = self._create_card(self.main_panel, "📝 Enter SQL Query")
        query_card.pack(fill=tk.X, pady=10)
        
        query_text = tk.Text(query_card, height=4, font=('Consolas', 11),
                            bg=self.theme['bg_secondary'], fg=self.theme['text_primary'],
                            insertbackground=self.theme['accent'])
        query_text.pack(fill=tk.X, padx=15, pady=5)
        query_text.insert('1.0', 'SELECT * FROM USERS')
        
        # Quick queries
        quick_frame = tk.Frame(query_card, bg=self.theme['bg_card'])
        quick_frame.pack(fill=tk.X, padx=15, pady=5)
        
        queries = [
            ("Users", "SELECT * FROM USERS"),
            ("Students", "SELECT * FROM STUDENT"),
            ("Courses", "SELECT * FROM COURSE"),
            ("Grades", "SELECT * FROM GRADES"),
            ("Tables", "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE'"),
        ]
        
        for name, sql in queries:
            btn = tk.Button(quick_frame, text=name, font=('Segoe UI', 9),
                           bg=self.theme['bg_secondary'], fg=self.theme['text_secondary'],
                           relief='flat', padx=10,
                           command=lambda q=sql: [query_text.delete('1.0', tk.END), query_text.insert('1.0', q)])
            btn.pack(side=tk.LEFT, padx=3)
        
        tk.Frame(query_card, height=10, bg=self.theme['bg_card']).pack()
        
        # Result area
        result_card = self._create_card(self.main_panel, "📊 Query Results")
        result_card.pack(fill=tk.BOTH, expand=True, pady=10)
        
        result_text = tk.Text(result_card, font=('Consolas', 10),
                             bg=self.theme['bg_secondary'], fg=self.theme['text_primary'],
                             wrap=tk.NONE)
        result_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        def execute_query():
            query = query_text.get('1.0', tk.END).strip()
            result_text.delete('1.0', tk.END)
            
            try:
                if query.upper().startswith('SELECT'):
                    results = self.db.fetch_all(query)
                    if results:
                        # Get columns
                        cols = list(results[0].keys())
                        result_text.insert(tk.END, " | ".join(str(c)[:15].ljust(15) for c in cols) + '\n')
                        result_text.insert(tk.END, "-" * (17 * len(cols)) + '\n')
                        
                        for row in results:
                            result_text.insert(tk.END, " | ".join(str(row.get(c, ''))[:15].ljust(15) for c in cols) + '\n')
                        
                        result_text.insert(tk.END, f"\n✅ {len(results)} row(s) returned")
                    else:
                        result_text.insert(tk.END, "No results")
                else:
                    result_text.insert(tk.END, "⚠️ Only SELECT queries allowed in viewer")
            except Exception as e:
                result_text.insert(tk.END, f"❌ Error: {e}")
        
        tk.Button(query_card, text="▶️ Execute Query", font=('Segoe UI', 10),
                 bg=self.theme['accent'], fg='#fff', relief='flat',
                 command=execute_query).pack(pady=10, ipadx=20, ipady=5)
    
    def _show_security_dashboard(self):
        """Show Security Dashboard - All 5 security models + Part B"""
        self._clear_panel()
        
        # Create and show security dashboard
        security_widget = SecurityDashboard(
            self.main_panel, 
            self.db, 
            self.theme, 
            self.user
        )
        security_widget.pack(fill='both', expand=True)
    
    def _show_settings(self):
        """Show settings."""
        self._clear_panel()
        
        tk.Label(self.main_panel, text="🔧 Settings",
                font=('Segoe UI', 18, 'bold'),
                bg=self.theme['bg_primary'], fg=self.theme['text_primary']).pack(anchor='w', pady=(0, 15))
        
        # Theme settings
        theme_card = self._create_card(self.main_panel, "🎨 Theme Settings")
        theme_card.pack(fill=tk.X, pady=10)
        
        tk.Label(theme_card, text="Select color theme:",
                bg=self.theme['bg_card'], fg=self.theme['text_secondary']).pack(anchor='w', padx=15, pady=5)
        
        theme_frame = tk.Frame(theme_card, bg=self.theme['bg_card'])
        theme_frame.pack(fill=tk.X, padx=15, pady=10)
        
        for theme in ColorThemes.get_all():
            btn = tk.Button(theme_frame, text=theme['name'], font=('Segoe UI', 10),
                           bg=theme['bg_secondary'], fg=theme['text_primary'],
                           relief='flat', padx=20, pady=8)
            btn.pack(side=tk.LEFT, padx=5)
        
        tk.Frame(theme_card, height=10, bg=self.theme['bg_card']).pack()
        
        # About
        about_card = self._create_card(self.main_panel, "ℹ️ About")
        about_card.pack(fill=tk.X, pady=10)
        
        about_text = """SRMS - Secure Student Records Management System
Database Security Term Project - Phase 2

Implements 5 Security Models:
• RBAC - Role-Based Access Control
• MLS - Multilevel Security (Bell-LaPadula)
• Encryption - AES-256 for sensitive data
• Inference Control - Prevent data deduction
• Flow Control - Prevent data downflow

Part B: Role Request Workflow Implementation"""
        
        tk.Label(about_card, text=about_text, justify=tk.LEFT,
                bg=self.theme['bg_card'], fg=self.theme['text_secondary']).pack(anchor='w', padx=15, pady=10)
        
        tk.Frame(about_card, height=10, bg=self.theme['bg_card']).pack()
    
    def _create_data_table(self, columns, data):
        """Create a styled data table."""
        # Table frame
        table_frame = tk.Frame(self.main_panel, bg=self.theme['bg_card'],
                              highlightthickness=1, highlightbackground=self.theme['border'])
        table_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Create treeview
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120, anchor='w')
        
        # Insert data
        for row in data:
            tree.insert('', tk.END, values=row)
        
        # Scrollbars
        v_scroll = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tree.yview)
        h_scroll = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        # Pack
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        return tree
