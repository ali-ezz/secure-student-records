"""
SRMS - Premium Modern GUI Application
Beautiful Design with SQL Server Backend
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.database.connection import get_database, is_sqlserver


from src.gui.admin_dashboard import AdminDashboard
from src.gui.instructor_dashboard import InstructorDashboard
from src.gui.ta_dashboard import TADashboard
from src.gui.student_dashboard import StudentDashboard
from src.gui.guest_dashboard import GuestDashboard

# Premium Color Themes
THEMES = {
    'dark': {
        'bg': '#0f0f1a', 'bg_primary': '#0f0f1a',
        'bg_secondary': '#1a1a2e',
        'card': '#16213e', 'bg_card': '#16213e',
        'card_hover': '#1f2b47',
        'accent': '#4361ee',
        'accent_light': '#4cc9f0',
        'text': '#ffffff', 'text_primary': '#ffffff',
        'text_secondary': '#8892b0',
        'success': '#00d26a',
        'error': '#ff4757',
        'warning': '#ffa502',
        'border': '#2d3561',
        'input_bg': '#0f0f1a',
    }
}

class PremiumApp:
    """Premium styled SRMS Application."""
    
    def __init__(self):
        self.theme = THEMES['dark']
        self.root = tk.Tk()
        self.root.title(" SRMS - Secure Student Records")
        self.root.geometry("1200x800")
        self.root.configure(bg=self.theme['bg'])
        self.root.minsize(1000, 700)
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - 1200) // 2
        y = (self.root.winfo_screenheight() - 800) // 2
        self.root.geometry(f"1200x800+{x}+{y}")
        
        self.current_user = None
        self._init_database()
        self._show_login()
    
    def _init_database(self):
        """Initialize database connection."""
        try:
            self.db = get_database()
            print("✓ Connected to", "SQL Server" if is_sqlserver() else "SQLite")
        except Exception as e:
            print(f"DB Error: {e}")
    
    def _clear(self):
        """Clear all widgets."""
        for w in self.root.winfo_children():
            w.destroy()
    
    def _show_login(self):
        """Show premium login screen."""
        self._clear()
        
        # Main container with gradient feel
        main = tk.Frame(self.root, bg=self.theme['bg'])
        main.pack(fill='both', expand=True)
        
        # Left side - Branding
        left = tk.Frame(main, bg=self.theme['bg_secondary'], width=450)
        left.pack(side='left', fill='y')
        left.pack_propagate(False)
        
        # Branding content
        brand = tk.Frame(left, bg=self.theme['bg_secondary'])
        brand.place(relx=0.5, rely=0.5, anchor='center')
        
        tk.Label(brand, text="🔐", font=('Segoe UI', 72),
                bg=self.theme['bg_secondary'], fg=self.theme['accent']).pack()
        tk.Label(brand, text="SRMS", font=('Segoe UI', 48, 'bold'),
                bg=self.theme['bg_secondary'], fg=self.theme['text']).pack(pady=(20, 5))
        tk.Label(brand, text="Secure Student Records\nManagement System",
                font=('Segoe UI', 14), justify='center',
                bg=self.theme['bg_secondary'], fg=self.theme['text_secondary']).pack(pady=10)
        
        # Security badges
        badges_frame = tk.Frame(brand, bg=self.theme['bg_secondary'])
        badges_frame.pack(pady=30)
        
        for badge in ['🛡️RBAC', '🔒MLS', '🔑AES-256', '📊SQL Server']:
            badge_label = tk.Label(badges_frame, text=badge,
                                   font=('Segoe UI', 10, 'bold'),
                                   bg=self.theme['card'], fg=self.theme['accent_light'],
                                   padx=12, pady=6)
            badge_label.pack(side='left', padx=5)
        
        # Right side - Login form
        right = tk.Frame(main, bg=self.theme['bg'])
        right.pack(side='right', fill='both', expand=True)
        
        # Center the form
        form_container = tk.Frame(right, bg=self.theme['bg'])
        form_container.place(relx=0.5, rely=0.5, anchor='center')
        
        # Login card
        card = tk.Frame(form_container, bg=self.theme['card'], padx=50, pady=40)
        card.pack()
        
        # Form header
        tk.Label(card, text="Welcome Back", font=('Segoe UI', 28, 'bold'),
                bg=self.theme['card'], fg=self.theme['text']).pack(anchor='w')
        tk.Label(card, text="Sign in to access your account",
                font=('Segoe UI', 12),
                bg=self.theme['card'], fg=self.theme['text_secondary']).pack(anchor='w', pady=(5, 30))
        
        # Username field
        tk.Label(card, text="USERNAME", font=('Segoe UI', 10, 'bold'),
                bg=self.theme['card'], fg=self.theme['text_secondary']).pack(anchor='w')
        
        username_frame = tk.Frame(card, bg=self.theme['input_bg'],
                                   highlightthickness=2, highlightbackground=self.theme['border'])
        username_frame.pack(fill='x', pady=(5, 20))
        
        tk.Label(username_frame, text="👤", font=('Segoe UI', 14),
                bg=self.theme['input_bg'], fg=self.theme['accent']).pack(side='left', padx=10)
        
        self.username_var = tk.StringVar()
        username_entry = tk.Entry(username_frame, textvariable=self.username_var,
                                   font=('Segoe UI', 14), width=25,
                                   bg=self.theme['input_bg'], fg=self.theme['text'],
                                   insertbackground=self.theme['accent'],
                                   relief='flat', border=0)
        username_entry.pack(side='left', pady=12, padx=5)
        username_entry.focus()
        
        # Password field
        tk.Label(card, text="PASSWORD", font=('Segoe UI', 10, 'bold'),
                bg=self.theme['card'], fg=self.theme['text_secondary']).pack(anchor='w')
        
        password_frame = tk.Frame(card, bg=self.theme['input_bg'],
                                   highlightthickness=2, highlightbackground=self.theme['border'])
        password_frame.pack(fill='x', pady=(5, 25))
        
        tk.Label(password_frame, text="🔑", font=('Segoe UI', 14),
                bg=self.theme['input_bg'], fg=self.theme['accent']).pack(side='left', padx=10)
        
        self.password_var = tk.StringVar()
        password_entry = tk.Entry(password_frame, textvariable=self.password_var,
                                   font=('Segoe UI', 14), width=25, show="●",
                                   bg=self.theme['input_bg'], fg=self.theme['text'],
                                   insertbackground=self.theme['accent'],
                                   relief='flat', border=0)
        password_entry.pack(side='left', pady=12, padx=5)
        password_entry.bind('<Return>', lambda e: self._do_login())
        
        # Status message
        self.status_var = tk.StringVar()
        self.status_label = tk.Label(card, textvariable=self.status_var,
                                      font=('Segoe UI', 11),
                                      bg=self.theme['card'], fg=self.theme['error'])
        self.status_label.pack(pady=(0, 15))
        
        # Login button - Premium gradient style
        login_btn = tk.Button(card, text="Sign In →", font=('Segoe UI', 14, 'bold'),
                              bg=self.theme['accent'], fg='#ffffff',
                              activebackground=self.theme['accent_light'],
                              relief='flat', cursor='hand2', width=25,
                              command=self._do_login)
        login_btn.pack(pady=(0, 15), ipady=12)
        
        # Hover effect for button
        login_btn.bind('<Enter>', lambda e: login_btn.config(bg=self.theme['accent_light']))
        login_btn.bind('<Leave>', lambda e: login_btn.config(bg=self.theme['accent']))
        
        # Guest access
        guest_btn = tk.Button(card, text="Continue as Guest",
                              font=('Segoe UI', 11),
                              bg=self.theme['card'], fg=self.theme['text_secondary'],
                              activebackground=self.theme['card_hover'],
                              relief='flat', cursor='hand2', width=25, border=0,
                              command=lambda: self._login_as('guest', 'guest123'))
        guest_btn.pack(ipady=8)
        
        # Demo accounts
        demo_frame = tk.Frame(card, bg=self.theme['card'])
        demo_frame.pack(pady=(30, 0))
        
        tk.Label(demo_frame, text="Demo Accounts:",
                font=('Segoe UI', 10, 'bold'),
                bg=self.theme['card'], fg=self.theme['text_secondary']).pack()
        
        accounts = [
            ('admin', 'Admin'),
            ('prof_smith', 'Instructor'),
            ('student1', 'Student'),
        ]
        
        acc_frame = tk.Frame(demo_frame, bg=self.theme['card'])
        acc_frame.pack(pady=10)
        
        for user, role in accounts:
            btn = tk.Button(acc_frame, text=f"{role}",
                           font=('Segoe UI', 9),
                           bg=self.theme['bg_secondary'], fg=self.theme['accent_light'],
                           relief='flat', cursor='hand2', padx=15, pady=5,
                           command=lambda u=user: self._login_as(u, f"{u.split('_')[0]}123" if '_' in u else f"{u}123"))
            btn.pack(side='left', padx=5)
    
    def _login_as(self, username, password):
        """Quick login helper."""
        self.username_var.set(username)
        self.password_var.set(password)
        self._do_login()
    
    def _do_login(self):
        """Perform login."""
        username = self.username_var.get().strip()
        password = self.password_var.get()
        
        if not username or not password:
            self.status_var.set("⚠️ Please enter username and password")
            return
        
        self.status_var.set("🔄 Authenticating...")
        self.status_label.config(fg=self.theme['accent'])
        self.root.update()
        
        try:
            if is_sqlserver():
                from src.database.sqlserver_auth import get_auth
                auth = get_auth()
                result = auth.authenticate(username, password)
                
                if result and isinstance(result, dict):
                    if 'error' in result:
                        self.status_var.set(f"❌ {result['error']}")
                        self.status_label.config(fg=self.theme['error'])
                    else:
                        self.status_var.set(f"✅ Welcome, {result['role']}!")
                        self.status_label.config(fg=self.theme['success'])
                        self.current_user = result
                        self.root.after(500, self._show_dashboard)
                else:
                    self.status_var.set("❌ Invalid credentials")
                    self.status_label.config(fg=self.theme['error'])
            else:
                from src.database.models import UserModel
                user_model = UserModel()
                user = user_model.authenticate(username, password)
                if user:
                    self.current_user = user
                    self._show_dashboard()
                else:
                    self.status_var.set("❌ Invalid credentials")
                    self.status_label.config(fg=self.theme['error'])
        except Exception as e:
            self.status_var.set(f"❌ Error: {str(e)[:40]}")
            self.status_label.config(fg=self.theme['error'])
    
    def _show_dashboard(self):
        """Show role-based dashboard using dedicated modules."""
        self._clear()
        
        role = self.current_user.get('role', 'Guest')
        
        # Main container
        main = tk.Frame(self.root, bg=self.theme['bg'])
        main.pack(fill='both', expand=True)
        
        # Instantiate appropriate dashboard
        dashboard = None
        
        try:
            if role == 'Admin':
                dashboard = AdminDashboard(main, self.current_user, self._show_login, theme=self.theme)
            elif role == 'Instructor':
                dashboard = InstructorDashboard(main, self.current_user, self._show_login, theme=self.theme)
            elif role == 'TA':
                dashboard = TADashboard(main, self.current_user, self._show_login, theme=self.theme)
            elif role == 'Student':
                dashboard = StudentDashboard(main, self.current_user, self._show_login, theme=self.theme)
            else:
                dashboard = GuestDashboard(main, self.current_user, self._show_login, theme=self.theme)
            
            # Pack it
            dashboard.pack(fill='both', expand=True)
            
        except Exception as e:
            messagebox.showerror("Dashboard Error", f"Failed to load dashboard: {e}")
            self._show_login()

    def run(self):
        """Run the application."""
        self.root.mainloop()


def main():
    print("\n" + "="*60)
    print("  🔐 SRMS - Premium Modern GUI")
    print("  Connected to SQL Server")
    print("="*60 + "\n")
    
    app = PremiumApp()
    app.run()


if __name__ == '__main__':
    main()
