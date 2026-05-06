"""
SRMS - Guest Dashboard
Guest view with minimal access (public course info only)
"""

import sys
import os
import tkinter as tk
from tkinter import ttk

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.database.connection import get_database, is_sqlserver


class GuestDashboard(ttk.Frame):
    """Guest Dashboard - public course info only."""
    
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
        
        # Main content
        content = ttk.Frame(self)
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Access restrictions panel
        self._create_access_panel(content)
        
        # Public courses list
        self._create_courses_panel(content)
    
    def _create_header(self):
        """Create header."""
        header = ttk.Frame(self)
        header.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(header, text="👁 Guest View", 
                  font=('Segoe UI', 18, 'bold')).pack(side=tk.LEFT)
        
        right_frame = ttk.Frame(header)
        right_frame.pack(side=tk.RIGHT)
        
        ttk.Label(right_frame, text="Clearance: 0 (Public Only) | ", 
                  font=('Segoe UI', 11)).pack(side=tk.LEFT)
        ttk.Label(right_frame, text="🔒 Limited Access", 
                  font=('Segoe UI', 10)).pack(side=tk.LEFT, padx=10)
        ttk.Button(right_frame, text="🚪 Exit", command=self.on_logout).pack(side=tk.LEFT)
        
        ttk.Separator(self, orient='horizontal').pack(fill=tk.X, padx=10)
    
    def _create_access_panel(self, parent):
        """Create access restrictions panel."""
        panel = ttk.LabelFrame(parent, text="🔐 Your Access Level")
        panel.pack(fill=tk.X, pady=10)
        
        ttk.Label(panel, text="As a Guest, you have PUBLIC access only (Clearance Level 0)",
                  font=('Segoe UI', 11, 'bold')).pack(pady=10)
        
        restrictions = [
            ("❌ USERS table", "DENIED - No access"),
            ("❌ STUDENT table", "DENIED - Confidential data"),
            ("❌ INSTRUCTOR table", "DENIED - Confidential data"),
            ("❌ GRADES table", "DENIED - Secret data"),
            ("❌ ATTENDANCE table", "DENIED - Secret data"),
            ("✅ COURSE table", "PublicInfo column ONLY (via view)"),
        ]
        
        for table, access in restrictions:
            row = ttk.Frame(panel)
            row.pack(fill=tk.X, pady=1, padx=10)
            ttk.Label(row, text=table, width=20, font=('Segoe UI', 10)).pack(side=tk.LEFT)
            ttk.Label(row, text=access, font=('Segoe UI', 10)).pack(side=tk.LEFT)
    
    def _create_courses_panel(self, parent):
        """Create public courses panel."""
        panel = ttk.LabelFrame(parent, text="📚 Available Courses (Public Info)")
        panel.pack(fill=tk.BOTH, expand=True, pady=10)
        
        ttk.Label(panel, text="These are publicly available courses:", 
                  font=('Segoe UI', 11)).pack(pady=5)
        
        columns = ('Code', 'Name', 'Department', 'Credits', 'Public Info')
        tree = ttk.Treeview(panel, columns=columns, show='headings', height=12)
        
        widths = [80, 150, 100, 60, 250]
        for col, w in zip(columns, widths):
            tree.heading(col, text=col)
            tree.column(col, width=w)
        
        try:
            if is_sqlserver():
                # Use the guest view or query public info only
                courses = self.db.fetch_all("""
                    SELECT CourseCode, CourseName, Department, Credits, PublicInfo
                    FROM COURSE 
                    WHERE IsActive = 1 AND ClassificationLevel <= 1
                """)
                
                for c in courses:
                    tree.insert('', tk.END, values=(
                        c['CourseCode'], c['CourseName'],
                        c.get('Department', ''), c.get('Credits', 3),
                        c.get('PublicInfo', 'No description')[:50]
                    ))
        except Exception as e:
            ttk.Label(panel, text=f"Error loading courses: {e}").pack()
        
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Register button
        ttk.Label(panel, 
                  text="💡 To access more features, please register as a Student",
                  font=('Segoe UI', 10)).pack(pady=10)
