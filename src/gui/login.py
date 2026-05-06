"""
SRMS - Enhanced Modern Login Form
Beautiful, professional login with animations and effects
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

try:
    import ttkbootstrap as ttk
    from ttkbootstrap.constants import *
    HAS_TTKBOOTSTRAP = True
except ImportError:
    HAS_TTKBOOTSTRAP = False

from config import THEME_COLORS, SecurityLevel
from src.database.models import UserModel
from src.database.connection import is_sqlserver

# Import SQL Server auth if available
try:
    from src.database.sqlserver_auth import get_auth
    HAS_SQLSERVER_AUTH = True
except ImportError:
    HAS_SQLSERVER_AUTH = False



class EnhancedLoginFrame(ttk.Frame):
    """Enhanced modern login form with visual effects."""
    
    def __init__(self, parent, on_success_callback):
        super().__init__(parent)
        self.on_success = on_success_callback
        self.user_model = UserModel()
        
        self._create_widgets()
        self._start_animations()
    
    def _create_widgets(self):
        """Create enhanced login form widgets."""
        # Configure grid for centering
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        # Main container
        main_container = ttk.Frame(self)
        main_container.grid(row=0, column=0)
        
        # ===== HEADER SECTION =====
        header_frame = ttk.Frame(main_container)
        header_frame.pack(pady=(0, 20))
        
        # Animated shield icon
        self.shield_var = tk.StringVar(value="🔐")
        shield_label = ttk.Label(
            header_frame,
            textvariable=self.shield_var,
            font=('Segoe UI', 64)
        )
        shield_label.pack()
        
        # Title with gradient effect simulation
        title_label = ttk.Label(
            header_frame,
            text="SRMS",
            font=('Segoe UI', 42, 'bold')
        )
        title_label.pack()
        
        subtitle_label = ttk.Label(
            header_frame,
            text="Secure Student Records Management System",
            font=('Segoe UI', 13)
        )
        subtitle_label.pack()
        
        # Security badges
        badges_frame = ttk.Frame(header_frame)
        badges_frame.pack(pady=10)
        
        badges = ['🛡️ RBAC', '🔒 MLS', '🔑 AES-256', '🚫 Inference', '⚡ Flow']
        for badge in badges:
            if HAS_TTKBOOTSTRAP:
                lbl = ttk.Label(badges_frame, text=badge, font=('Segoe UI', 9), bootstyle="info")
            else:
                lbl = ttk.Label(badges_frame, text=badge, font=('Segoe UI', 9))
            lbl.pack(side=tk.LEFT, padx=5)
        
        # ===== LOGIN CARD =====
        if HAS_TTKBOOTSTRAP:
            login_card = ttk.Labelframe(main_container, text="", bootstyle="dark")
        else:
            login_card = ttk.Labelframe(main_container, text="")
        login_card.pack(padx=30, pady=10, ipadx=50, ipady=30)
        
        # Welcome message
        welcome_frame = ttk.Frame(login_card)
        welcome_frame.pack(pady=(0, 20))
        
        ttk.Label(
            welcome_frame,
            text="Welcome Back! 👋",
            font=('Segoe UI', 20, 'bold')
        ).pack()
        
        ttk.Label(
            welcome_frame,
            text="Sign in to access your account",
            font=('Segoe UI', 10)
        ).pack()
        
        # Username Field with icon
        username_frame = ttk.Frame(login_card)
        username_frame.pack(fill=tk.X, pady=8)
        
        username_label_frame = ttk.Frame(username_frame)
        username_label_frame.pack(anchor=tk.W)
        ttk.Label(username_label_frame, text="👤", font=('Segoe UI', 12)).pack(side=tk.LEFT)
        ttk.Label(username_label_frame, text=" Username", font=('Segoe UI', 11)).pack(side=tk.LEFT)
        
        self.username_var = tk.StringVar()
        if HAS_TTKBOOTSTRAP:
            self.username_entry = ttk.Entry(
                username_frame,
                textvariable=self.username_var,
                font=('Segoe UI', 13),
                width=30,
                bootstyle="light"
            )
        else:
            self.username_entry = ttk.Entry(
                username_frame,
                textvariable=self.username_var,
                font=('Segoe UI', 13),
                width=30
            )
        self.username_entry.pack(fill=tk.X, pady=(5, 0), ipady=5)
        self.username_entry.focus()
        
        # Password Field with icon and show/hide
        password_frame = ttk.Frame(login_card)
        password_frame.pack(fill=tk.X, pady=8)
        
        password_label_frame = ttk.Frame(password_frame)
        password_label_frame.pack(anchor=tk.W)
        ttk.Label(password_label_frame, text="🔑", font=('Segoe UI', 12)).pack(side=tk.LEFT)
        ttk.Label(password_label_frame, text=" Password", font=('Segoe UI', 11)).pack(side=tk.LEFT)
        
        password_input_frame = ttk.Frame(password_frame)
        password_input_frame.pack(fill=tk.X)
        
        self.password_var = tk.StringVar()
        self.show_password = False
        
        if HAS_TTKBOOTSTRAP:
            self.password_entry = ttk.Entry(
                password_input_frame,
                textvariable=self.password_var,
                font=('Segoe UI', 13),
                show="•",
                bootstyle="light"
            )
        else:
            self.password_entry = ttk.Entry(
                password_input_frame,
                textvariable=self.password_var,
                font=('Segoe UI', 13),
                show="•"
            )
        self.password_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=(5, 0), ipady=5)
        
        # Show/Hide password button
        self.show_btn_text = tk.StringVar(value="👁")
        if HAS_TTKBOOTSTRAP:
            show_btn = ttk.Button(
                password_input_frame,
                textvariable=self.show_btn_text,
                command=self._toggle_password,
                width=3,
                bootstyle="secondary-outline"
            )
        else:
            show_btn = ttk.Button(
                password_input_frame,
                textvariable=self.show_btn_text,
                command=self._toggle_password,
                width=3
            )
        show_btn.pack(side=tk.LEFT, padx=(5, 0), pady=(5, 0))
        
        # Remember me checkbox
        remember_frame = ttk.Frame(login_card)
        remember_frame.pack(fill=tk.X, pady=5)
        
        self.remember_var = tk.BooleanVar()
        ttk.Checkbutton(
            remember_frame,
            text="Remember me",
            variable=self.remember_var
        ).pack(side=tk.LEFT)
        
        # Buttons
        button_frame = ttk.Frame(login_card)
        button_frame.pack(fill=tk.X, pady=(20, 5))
        
        if HAS_TTKBOOTSTRAP:
            self.login_btn = ttk.Button(
                button_frame,
                text="🔓  Sign In",
                command=self._login,
                bootstyle="success",
                width=28
            )
        else:
            self.login_btn = ttk.Button(
                button_frame,
                text="Sign In",
                command=self._login,
                width=28
            )
        self.login_btn.pack(pady=5, ipady=8)
        
        # Or separator
        separator_frame = ttk.Frame(login_card)
        separator_frame.pack(fill=tk.X, pady=10)
        
        ttk.Separator(separator_frame, orient='horizontal').pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(separator_frame, text=" or ", font=('Segoe UI', 9)).pack(side=tk.LEFT)
        ttk.Separator(separator_frame, orient='horizontal').pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Guest button
        if HAS_TTKBOOTSTRAP:
            self.guest_btn = ttk.Button(
                login_card,
                text="👁  Continue as Guest",
                command=self._guest_login,
                bootstyle="info-outline",
                width=28
            )
        else:
            self.guest_btn = ttk.Button(
                login_card,
                text="Continue as Guest",
                command=self._guest_login,
                width=28
            )
        self.guest_btn.pack(pady=5, ipady=5)
        
        # Status/Loading indicator
        self.status_frame = ttk.Frame(login_card)
        self.status_frame.pack(pady=10)
        
        self.status_var = tk.StringVar()
        self.status_label = ttk.Label(
            self.status_frame,
            textvariable=self.status_var,
            font=('Segoe UI', 10)
        )
        self.status_label.pack()
        
        # Bind keys
        self.password_entry.bind('<Return>', lambda e: self._login())
        self.username_entry.bind('<Return>', lambda e: self.password_entry.focus())
        
        # ===== DEMO ACCOUNTS SECTION =====
        demo_frame = ttk.Frame(main_container)
        demo_frame.pack(pady=20)
        
        ttk.Label(
            demo_frame,
            text="📋 Demo Accounts",
            font=('Segoe UI', 11, 'bold')
        ).pack()
        
        # Demo accounts in a nice table
        accounts_frame = ttk.Frame(demo_frame)
        accounts_frame.pack(pady=5)
        
        demo_accounts = [
            ('admin', 'admin123', 'Admin', '🔴'),
            ('prof_smith', 'prof123', 'Instructor', '🟠'),
            ('ta_williams', 'ta123', 'TA', '🟡'),
            ('student1', 'student123', 'Student', '🟢'),
            ('guest', 'guest123', 'Guest', '⚪')
        ]
        
        for i, (user, pwd, role, color) in enumerate(demo_accounts):
            row_frame = ttk.Frame(accounts_frame)
            row_frame.pack(anchor=tk.W)
            
            ttk.Label(row_frame, text=f"{color} {role}:", width=12, font=('Segoe UI', 9)).pack(side=tk.LEFT)
            ttk.Label(row_frame, text=f"{user} / {pwd}", font=('Consolas', 9)).pack(side=tk.LEFT)
        
        # ===== FOOTER =====
        footer_frame = ttk.Frame(main_container)
        footer_frame.pack(pady=10)
        
        self.time_var = tk.StringVar()
        ttk.Label(
            footer_frame,
            textvariable=self.time_var,
            font=('Segoe UI', 9)
        ).pack()
        
        ttk.Label(
            footer_frame,
            text="🔒 Connection Secured • AES-256 Encrypted",
            font=('Segoe UI', 9)
        ).pack()
    
    def _toggle_password(self):
        """Toggle password visibility."""
        self.show_password = not self.show_password
        if self.show_password:
            self.password_entry.configure(show="")
            self.show_btn_text.set("🔒")
        else:
            self.password_entry.configure(show="•")
            self.show_btn_text.set("👁")
    
    def _start_animations(self):
        """Start subtle animations."""
        self._update_time()
        self._animate_shield()
    
    def _update_time(self):
        """Update time display."""
        now = datetime.now().strftime('%H:%M:%S • %B %d, %Y')
        self.time_var.set(f"🕐 {now}")
        self.after(1000, self._update_time)
    
    def _animate_shield(self):
        """Animate shield icon."""
        shields = ['🔐', '🔒', '🛡️', '🔒', '🔐']
        current = self.shield_var.get()
        idx = (shields.index(current) + 1) % len(shields) if current in shields else 0
        self.shield_var.set(shields[idx])
        self.after(2000, self._animate_shield)
    
    def _login(self):
        """Attempt to login with loading effect."""
        username = self.username_var.get().strip()
        password = self.password_var.get()
        
        if not username or not password:
            self.status_var.set("❌ Please enter username and password")
            self.status_label.configure(foreground='red')
            self._shake_widget(self.username_entry)
            return
        
        # Loading animation
        self.login_btn.configure(state='disabled')
        self._show_loading()
        
        self.after(800, lambda: self._perform_login(username, password))
    
    def _show_loading(self):
        """Show loading animation."""
        self.loading_dots = 0
        self._animate_loading()
    
    def _animate_loading(self):
        """Animate loading dots."""
        if self.login_btn['state'] == 'disabled':
            dots = '.' * (self.loading_dots % 4)
            self.status_var.set(f"🔄 Authenticating{dots}")
            self.status_label.configure(foreground='#0dcaf0')
            self.loading_dots += 1
            self.after(200, self._animate_loading)
    
    def _perform_login(self, username: str, password: str):
        """Perform actual login."""
        user = None
        error_msg = None
        
        # Use SQL Server auth if available and configured
        if HAS_SQLSERVER_AUTH and is_sqlserver():
            auth = get_auth()
            result = auth.authenticate(username, password)
            if result and isinstance(result, dict):
                if 'error' in result:
                    error_msg = result['error']
                else:
                    user = result
        else:
            # Fallback to SQLite
            user = self.user_model.authenticate(username, password)
        
        self.login_btn.configure(state='normal')
        
        if user:
            self.status_var.set(f"✅ Welcome, {user['role']}!")
            self.status_label.configure(foreground='green')
            self.after(600, lambda: self.on_success(user))
        else:
            if error_msg:
                self.status_var.set(f"❌ {error_msg}")
            else:
                self.status_var.set("❌ Invalid credentials")
            self.status_label.configure(foreground='red')
            self.password_var.set("")
            self._shake_widget(self.password_entry)
    
    def _shake_widget(self, widget):
        """Shake widget for error feedback."""
        original_x = widget.winfo_x()
        
        def shake(count, direction):
            if count > 0:
                offset = 5 * direction
                widget.place(x=original_x + offset)
                self.after(50, lambda: shake(count - 1, -direction))
            else:
                widget.place(x=original_x)
        
        # Only shake if place geometry manager is used
        try:
            shake(4, 1)
        except:
            pass
    
    def _guest_login(self):
        """Login as guest."""
        user = None
        
        # Use SQL Server auth if available
        if HAS_SQLSERVER_AUTH and is_sqlserver():
            auth = get_auth()
            result = auth.authenticate('guest', 'guest123')
            if result and isinstance(result, dict) and 'error' not in result:
                user = result
        else:
            user = self.user_model.authenticate('guest', 'guest123')
        
        if user:
            self.on_success(user)
        else:
            # Guest already exists in SQL Server database
            self.status_var.set("❌ Guest login failed")
            self.status_label.configure(foreground='red')


# Use enhanced login as default
LoginFrame = EnhancedLoginFrame
