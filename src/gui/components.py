"""
SRMS - Shared GUI Components
Reusable UI widgets with enhanced functionality
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

try:
    import ttkbootstrap as ttk
    from ttkbootstrap.constants import *
    from ttkbootstrap.tooltip import ToolTip
    HAS_TTKBOOTSTRAP = True
except ImportError:
    HAS_TTKBOOTSTRAP = False


class SearchableTreeview(ttk.Frame):
    """Treeview with search/filter and export capabilities."""
    
    def __init__(self, parent, columns, data_callback=None, **kwargs):
        super().__init__(parent)
        self.columns = columns
        self.data_callback = data_callback
        self.all_data = []
        
        self._create_widgets(**kwargs)
    
    def _create_widgets(self, **kwargs):
        """Create search bar and treeview."""
        # Search bar
        search_frame = ttk.Frame(self)
        search_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(search_frame, text="🔍").pack(side=tk.LEFT, padx=5)
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self._on_search)
        
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=5)
        
        # Export button
        if HAS_TTKBOOTSTRAP:
            export_btn = ttk.Button(search_frame, text="📤 Export CSV", 
                                     command=self._export_csv, bootstyle="info-outline")
        else:
            export_btn = ttk.Button(search_frame, text="Export", command=self._export_csv)
        export_btn.pack(side=tk.RIGHT, padx=5)
        
        # Treeview with scrollbar
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        self.tree = ttk.Treeview(tree_frame, columns=self.columns, show='headings',
                                  height=kwargs.get('height', 15))
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        # Configure columns
        for col in self.columns:
            self.tree.heading(col, text=col, command=lambda c=col: self._sort_column(c))
            self.tree.column(col, width=100)
        
        # Status bar
        self.status_var = tk.StringVar(value="0 items")
        status_label = ttk.Label(self, textvariable=self.status_var, font=('Segoe UI', 9))
        status_label.pack(anchor=tk.W, pady=(5, 0))
    
    def load_data(self, data):
        """Load data into treeview."""
        self.all_data = data
        self._populate_tree(data)
    
    def _populate_tree(self, data):
        """Populate tree with data."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for row in data:
            self.tree.insert('', 'end', values=row)
        
        self.status_var.set(f"{len(data)} items")
    
    def _on_search(self, *args):
        """Filter data based on search."""
        query = self.search_var.get().lower()
        if not query:
            self._populate_tree(self.all_data)
            return
        
        filtered = []
        for row in self.all_data:
            if any(query in str(cell).lower() for cell in row):
                filtered.append(row)
        
        self._populate_tree(filtered)
    
    def _sort_column(self, col):
        """Sort by column."""
        col_idx = self.columns.index(col)
        data = [(self.tree.set(child, col), child) for child in self.tree.get_children()]
        
        try:
            data.sort(key=lambda x: float(x[0]) if x[0].replace('.', '').isdigit() else x[0].lower())
        except:
            data.sort(key=lambda x: x[0].lower())
        
        for idx, (_, child) in enumerate(data):
            self.tree.move(child, '', idx)
    
    def _export_csv(self):
        """Export data to CSV file."""
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if not filename:
            return
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(self.columns)
            for child in self.tree.get_children():
                writer.writerow(self.tree.item(child)['values'])
        
        messagebox.showinfo("Export Complete", f"Data exported to {filename}")
    
    def get_selected(self):
        """Get selected item values."""
        selection = self.tree.selection()
        if selection:
            return self.tree.item(selection[0])['values']
        return None
    
    def bind_double_click(self, callback):
        """Bind double-click event."""
        self.tree.bind('<Double-1>', callback)


class StatsCard(ttk.Frame):
    """Statistics card with icon and animation."""
    
    def __init__(self, parent, icon, title, value="0", color="primary"):
        if HAS_TTKBOOTSTRAP:
            super().__init__(parent, bootstyle="dark")
        else:
            super().__init__(parent, relief='raised', borderwidth=2)
        
        self.color = color
        self._create_widgets(icon, title, value)
    
    def _create_widgets(self, icon, title, value):
        """Create card widgets."""
        # Icon
        icon_label = ttk.Label(self, text=icon, font=('Segoe UI', 24))
        icon_label.pack(pady=(15, 5))
        
        # Value
        self.value_label = ttk.Label(self, text=value, font=('Segoe UI', 32, 'bold'))
        self.value_label.pack()
        
        # Title
        title_label = ttk.Label(self, text=title, font=('Segoe UI', 11))
        title_label.pack(pady=(5, 15))
    
    def set_value(self, value):
        """Update the value."""
        self.value_label.config(text=str(value))


class NotificationBell(ttk.Frame):
    """Notification bell indicator with popup."""
    
    def __init__(self, parent, on_click=None):
        super().__init__(parent)
        self.on_click = on_click
        self.count = 0
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create bell and badge."""
        self.bell_btn = ttk.Button(self, text="🔔", command=self._show_notifications)
        self.bell_btn.pack()
        
        self.count_var = tk.StringVar(value="")
        self.badge = ttk.Label(self, textvariable=self.count_var, 
                               foreground='red', font=('Segoe UI', 8, 'bold'))
        self.badge.place(x=20, y=0)
    
    def set_count(self, count):
        """Set notification count."""
        self.count = count
        self.count_var.set(str(count) if count > 0 else "")
    
    def _show_notifications(self):
        """Show notifications popup."""
        if self.on_click:
            self.on_click()


class PasswordStrengthMeter(ttk.Frame):
    """Password strength indicator."""
    
    def __init__(self, parent, password_var):
        super().__init__(parent)
        self.password_var = password_var
        self.password_var.trace('w', self._check_strength)
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create strength meter."""
        self.strength_var = tk.StringVar(value="")
        self.strength_label = ttk.Label(self, textvariable=self.strength_var, font=('Segoe UI', 9))
        self.strength_label.pack(anchor=tk.W)
        
        if HAS_TTKBOOTSTRAP:
            self.progress = ttk.Progressbar(self, length=200, mode='determinate', bootstyle="success-striped")
        else:
            self.progress = ttk.Progressbar(self, length=200, mode='determinate')
        self.progress.pack(fill=tk.X)
    
    def _check_strength(self, *args):
        """Check password strength."""
        password = self.password_var.get()
        score = 0
        
        if len(password) >= 8: score += 25
        if any(c.isupper() for c in password): score += 25
        if any(c.isdigit() for c in password): score += 25
        if any(c in '!@#$%^&*()_+-=' for c in password): score += 25
        
        self.progress['value'] = score
        
        if score <= 25:
            self.strength_var.set("Weak")
        elif score <= 50:
            self.strength_var.set("Fair")
        elif score <= 75:
            self.strength_var.set("Good")
        else:
            self.strength_var.set("Strong")


class DatePicker(ttk.Frame):
    """Simple date picker."""
    
    def __init__(self, parent, date_var=None):
        super().__init__(parent)
        self.date_var = date_var or tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create date entry and buttons."""
        entry = ttk.Entry(self, textvariable=self.date_var, width=12)
        entry.pack(side=tk.LEFT)
        
        if HAS_TTKBOOTSTRAP:
            prev_btn = ttk.Button(self, text="◀", width=3, command=self._prev_day, bootstyle="outline")
            next_btn = ttk.Button(self, text="▶", width=3, command=self._next_day, bootstyle="outline")
        else:
            prev_btn = ttk.Button(self, text="<", width=2, command=self._prev_day)
            next_btn = ttk.Button(self, text=">", width=2, command=self._next_day)
        
        prev_btn.pack(side=tk.LEFT, padx=2)
        next_btn.pack(side=tk.LEFT)
    
    def _prev_day(self):
        """Go to previous day."""
        try:
            from datetime import timedelta
            current = datetime.strptime(self.date_var.get(), '%Y-%m-%d')
            self.date_var.set((current - timedelta(days=1)).strftime('%Y-%m-%d'))
        except:
            pass
    
    def _next_day(self):
        """Go to next day."""
        try:
            from datetime import timedelta
            current = datetime.strptime(self.date_var.get(), '%Y-%m-%d')
            self.date_var.set((current + timedelta(days=1)).strftime('%Y-%m-%d'))
        except:
            pass
    
    def get(self):
        return self.date_var.get()


class StatusBar(ttk.Frame):
    """Application status bar with security info."""
    
    def __init__(self, parent, user=None):
        super().__init__(parent)
        self.user = user
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create status bar widgets."""
        # Left - Security status
        left_frame = ttk.Frame(self)
        left_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.security_var = tk.StringVar(value="🔒 All security models active")
        ttk.Label(left_frame, textvariable=self.security_var, font=('Segoe UI', 9)).pack(side=tk.LEFT, padx=10)
        
        # Center - Connection status
        self.db_var = tk.StringVar(value="📊 Database: Connected")
        ttk.Label(left_frame, textvariable=self.db_var, font=('Segoe UI', 9)).pack(side=tk.LEFT, padx=10)
        
        # Right - Time
        right_frame = ttk.Frame(self)
        right_frame.pack(side=tk.RIGHT)
        
        self.time_var = tk.StringVar()
        ttk.Label(right_frame, textvariable=self.time_var, font=('Segoe UI', 9)).pack(side=tk.RIGHT, padx=10)
        
        self._update_time()
    
    def _update_time(self):
        """Update time display."""
        self.time_var.set(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        self.after(1000, self._update_time)
    
    def set_message(self, message):
        """Set status message."""
        self.security_var.set(message)


class ConfirmDialog:
    """Custom confirmation dialog."""
    
    @staticmethod
    def ask(parent, title, message, icon="question"):
        """Show confirmation dialog."""
        return messagebox.askyesno(title, message)
    
    @staticmethod
    def ask_with_input(parent, title, message, default=""):
        """Show dialog with input field."""
        dialog = tk.Toplevel(parent)
        dialog.title(title)
        dialog.geometry("400x150")
        dialog.transient(parent)
        dialog.grab_set()
        
        ttk.Label(dialog, text=message).pack(pady=10)
        
        input_var = tk.StringVar(value=default)
        entry = ttk.Entry(dialog, textvariable=input_var, width=40)
        entry.pack(pady=5)
        entry.focus()
        
        result = [None]
        
        def on_ok():
            result[0] = input_var.get()
            dialog.destroy()
        
        def on_cancel():
            dialog.destroy()
        
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=15)
        
        ttk.Button(btn_frame, text="OK", command=on_ok).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Cancel", command=on_cancel).pack(side=tk.LEFT)
        
        dialog.wait_window()
        return result[0]
