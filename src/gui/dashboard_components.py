"""
SRMS - Enhanced Dashboard Header and Status Bar
Professional header with notifications, search, and status bar
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


class EnhancedHeader(ttk.Frame):
    """Enhanced dashboard header with user info, notifications, and quick actions."""
    
    def __init__(self, parent, user: dict, title: str = "Dashboard",
                 on_logout=None, on_profile=None, on_search=None, on_notifications=None):
        super().__init__(parent)
        
        self.user = user
        self.title = title
        self.on_logout = on_logout
        self.on_profile = on_profile
        self.on_search = on_search
        self.on_notifications = on_notifications
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create header widgets."""
        # Configure padding
        self.pack(fill=tk.X)
        
        # Left section - Title and role badge
        left_frame = ttk.Frame(self)
        left_frame.pack(side=tk.LEFT, padx=15, pady=10)
        
        # Icon based on role
        role_icons = {
            'Admin': '👑',
            'Instructor': '👨‍🏫',
            'TA': '📋',
            'Student': '🎓',
            'Guest': '👁'
        }
        icon = role_icons.get(self.user.get('role', 'Guest'), '👤')
        
        title_text = f"{icon} {self.title}"
        ttk.Label(left_frame, text=title_text, font=('Segoe UI', 18, 'bold')).pack(side=tk.LEFT)
        
        # Security level badge
        level = self.user.get('clearance_level', 0)
        level_colors = {4: 'danger', 3: 'warning', 2: 'info', 1: 'success', 0: 'secondary'}
        level_names = {4: 'TOP SECRET', 3: 'SECRET', 2: 'CONFIDENTIAL', 1: 'UNCLASSIFIED', 0: 'PUBLIC'}
        
        if HAS_TTKBOOTSTRAP:
            level_badge = ttk.Label(
                left_frame,
                text=f" {level_names.get(level, 'UNKNOWN')} ",
                font=('Segoe UI', 9, 'bold'),
                bootstyle=level_colors.get(level, 'secondary')
            )
        else:
            level_badge = ttk.Label(
                left_frame,
                text=f"[{level_names.get(level, 'UNKNOWN')}]",
                font=('Segoe UI', 9, 'bold')
            )
        level_badge.pack(side=tk.LEFT, padx=15)
        
        # Center section - Search bar
        if self.on_search:
            center_frame = ttk.Frame(self)
            center_frame.pack(side=tk.LEFT, expand=True, padx=20)
            
            search_frame = ttk.Frame(center_frame)
            search_frame.pack()
            
            ttk.Label(search_frame, text="🔍", font=('Segoe UI', 12)).pack(side=tk.LEFT)
            
            self.search_var = tk.StringVar()
            if HAS_TTKBOOTSTRAP:
                search_entry = ttk.Entry(
                    search_frame,
                    textvariable=self.search_var,
                    width=30,
                    bootstyle="light"
                )
            else:
                search_entry = ttk.Entry(
                    search_frame,
                    textvariable=self.search_var,
                    width=30
                )
            search_entry.pack(side=tk.LEFT, padx=5)
            search_entry.bind('<Return>', lambda e: self._do_search())
            
            if HAS_TTKBOOTSTRAP:
                ttk.Button(
                    search_frame,
                    text="Search",
                    command=self._do_search,
                    bootstyle="info-outline",
                    width=8
                ).pack(side=tk.LEFT)
            else:
                ttk.Button(
                    search_frame,
                    text="Search",
                    command=self._do_search,
                    width=8
                ).pack(side=tk.LEFT)
        
        # Right section - User info and actions
        right_frame = ttk.Frame(self)
        right_frame.pack(side=tk.RIGHT, padx=15, pady=10)
        
        # Notification bell
        if self.on_notifications:
            self.notif_count = tk.StringVar(value="🔔")
            if HAS_TTKBOOTSTRAP:
                notif_btn = ttk.Button(
                    right_frame,
                    textvariable=self.notif_count,
                    command=self.on_notifications,
                    bootstyle="warning-outline",
                    width=4
                )
            else:
                notif_btn = ttk.Button(
                    right_frame,
                    textvariable=self.notif_count,
                    command=self.on_notifications,
                    width=4
                )
            notif_btn.pack(side=tk.LEFT, padx=5)
        
        # User info
        user_info = ttk.Frame(right_frame)
        user_info.pack(side=tk.LEFT, padx=10)
        
        ttk.Label(
            user_info,
            text=f"👤 {self.user.get('username', 'User')}",
            font=('Segoe UI', 11)
        ).pack(side=tk.LEFT)
        
        ttk.Label(
            user_info,
            text=f" ({self.user.get('role', 'Guest')})",
            font=('Segoe UI', 10)
        ).pack(side=tk.LEFT)
        
        # Profile button
        if self.on_profile:
            if HAS_TTKBOOTSTRAP:
                ttk.Button(
                    right_frame,
                    text="⚙️ Profile",
                    command=self.on_profile,
                    bootstyle="info-outline",
                    width=10
                ).pack(side=tk.LEFT, padx=5)
            else:
                ttk.Button(
                    right_frame,
                    text="Profile",
                    command=self.on_profile,
                    width=10
                ).pack(side=tk.LEFT, padx=5)
        
        # Logout button
        if self.on_logout:
            if HAS_TTKBOOTSTRAP:
                ttk.Button(
                    right_frame,
                    text="🚪 Logout",
                    command=self.on_logout,
                    bootstyle="danger-outline",
                    width=10
                ).pack(side=tk.LEFT, padx=5)
            else:
                ttk.Button(
                    right_frame,
                    text="Logout",
                    command=self.on_logout,
                    width=10
                ).pack(side=tk.LEFT, padx=5)
    
    def _do_search(self):
        """Perform search."""
        if self.on_search:
            self.on_search(self.search_var.get())
    
    def update_notifications(self, count: int):
        """Update notification count."""
        if count > 0:
            self.notif_count.set(f"🔔{count}")
        else:
            self.notif_count.set("🔔")


class EnhancedStatusBar(ttk.Frame):
    """Enhanced status bar with system info and quick stats."""
    
    def __init__(self, parent, user: dict):
        super().__init__(parent)
        self.user = user
        
        self._create_widgets()
        self._update_time()
    
    def _create_widgets(self):
        """Create status bar widgets."""
        # Left - Connection status
        left_frame = ttk.Frame(self)
        left_frame.pack(side=tk.LEFT, padx=10, pady=5)
        
        self.status_var = tk.StringVar(value="🟢 Connected")
        ttk.Label(left_frame, textvariable=self.status_var, font=('Segoe UI', 9)).pack(side=tk.LEFT)
        
        ttk.Separator(left_frame, orient='vertical').pack(side=tk.LEFT, padx=10, fill='y')
        
        ttk.Label(left_frame, text="🔒 Encrypted", font=('Segoe UI', 9)).pack(side=tk.LEFT)
        
        # Center - Messages
        center_frame = ttk.Frame(self)
        center_frame.pack(side=tk.LEFT, expand=True, padx=10)
        
        self.message_var = tk.StringVar(value="")
        self.message_label = ttk.Label(center_frame, textvariable=self.message_var, font=('Segoe UI', 9))
        self.message_label.pack()
        
        # Right - Time and session info
        right_frame = ttk.Frame(self)
        right_frame.pack(side=tk.RIGHT, padx=10, pady=5)
        
        self.time_var = tk.StringVar()
        ttk.Label(right_frame, textvariable=self.time_var, font=('Segoe UI', 9)).pack(side=tk.RIGHT)
        
        ttk.Separator(right_frame, orient='vertical').pack(side=tk.RIGHT, padx=10, fill='y')
        
        ttk.Label(
            right_frame,
            text=f"Session: {self.user.get('username', 'Guest')}",
            font=('Segoe UI', 9)
        ).pack(side=tk.RIGHT)
    
    def _update_time(self):
        """Update time display."""
        now = datetime.now().strftime('%H:%M:%S')
        self.time_var.set(f"🕐 {now}")
        self.after(1000, self._update_time)
    
    def set_message(self, message: str, type_: str = 'info'):
        """Set status bar message."""
        icons = {'info': 'ℹ️', 'success': '✅', 'warning': '⚠️', 'error': '❌'}
        icon = icons.get(type_, 'ℹ️')
        self.message_var.set(f"{icon} {message}")
        
        # Auto-clear after 5 seconds
        self.after(5000, lambda: self.message_var.set(""))
    
    def set_status(self, connected: bool):
        """Set connection status."""
        if connected:
            self.status_var.set("🟢 Connected")
        else:
            self.status_var.set("🔴 Disconnected")


class QuickActionsPanel(ttk.Frame):
    """Quick actions floating panel."""
    
    def __init__(self, parent, actions: list):
        super().__init__(parent)
        
        self.actions = actions
        self._create_widgets()
    
    def _create_widgets(self):
        """Create quick action buttons."""
        ttk.Label(self, text="⚡ Quick Actions", font=('Segoe UI', 11, 'bold')).pack(pady=5)
        
        for action in self.actions:
            if action.get('separator'):
                ttk.Separator(self, orient='horizontal').pack(fill=tk.X, pady=5, padx=10)
                continue
            
            if HAS_TTKBOOTSTRAP:
                btn = ttk.Button(
                    self,
                    text=f"{action.get('icon', '')} {action['label']}",
                    command=action.get('command', lambda: None),
                    bootstyle=action.get('style', 'secondary-outline'),
                    width=20
                )
            else:
                btn = ttk.Button(
                    self,
                    text=action['label'],
                    command=action.get('command', lambda: None),
                    width=20
                )
            btn.pack(pady=2, padx=10)


class WelcomeCard(ttk.Frame):
    """Welcome card with user summary."""
    
    def __init__(self, parent, user: dict):
        super().__init__(parent)
        self.user = user
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create welcome card."""
        # Greeting based on time
        hour = datetime.now().hour
        if hour < 12:
            greeting = "Good Morning"
            icon = "🌅"
        elif hour < 17:
            greeting = "Good Afternoon"
            icon = "☀️"
        else:
            greeting = "Good Evening"
            icon = "🌙"
        
        # Welcome message
        ttk.Label(
            self,
            text=f"{icon} {greeting}, {self.user.get('username', 'User')}!",
            font=('Segoe UI', 20, 'bold')
        ).pack(anchor='w', pady=(0, 5))
        
        # Role and last login
        info_frame = ttk.Frame(self)
        info_frame.pack(anchor='w')
        
        ttk.Label(
            info_frame,
            text=f"Role: {self.user.get('role', 'Guest')}",
            font=('Segoe UI', 11)
        ).pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Label(
            info_frame,
            text=f"Clearance Level: {self.user.get('clearance_level', 0)}",
            font=('Segoe UI', 11)
        ).pack(side=tk.LEFT, padx=(0, 20))
        
        # Today's date
        today = datetime.now().strftime('%A, %B %d, %Y')
        ttk.Label(
            self,
            text=f"📅 {today}",
            font=('Segoe UI', 10)
        ).pack(anchor='w', pady=(10, 0))


class DashboardSummary(ttk.Frame):
    """Dashboard summary with stats cards."""
    
    def __init__(self, parent, stats: list):
        """
        Args:
            stats: List of {'icon', 'title', 'value', 'color', 'trend'}
        """
        super().__init__(parent)
        self.stats = stats
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create summary cards."""
        for i, stat in enumerate(self.stats):
            card = self._create_stat_card(stat)
            card.grid(row=0, column=i, padx=10, pady=10, sticky='nsew')
            self.columnconfigure(i, weight=1)
    
    def _create_stat_card(self, stat: dict):
        """Create individual stat card."""
        if HAS_TTKBOOTSTRAP:
            card = ttk.Frame(self, bootstyle=stat.get('color', 'dark'))
        else:
            card = ttk.Frame(self, relief='raised', borderwidth=1)
        
        inner = ttk.Frame(card)
        inner.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Icon and title
        header = ttk.Frame(inner)
        header.pack(fill=tk.X)
        
        ttk.Label(
            header,
            text=stat.get('icon', '📊'),
            font=('Segoe UI', 24)
        ).pack(side=tk.LEFT)
        
        ttk.Label(
            header,
            text=stat.get('title', 'Stat'),
            font=('Segoe UI', 10)
        ).pack(side=tk.LEFT, padx=10)
        
        # Value
        ttk.Label(
            inner,
            text=str(stat.get('value', 0)),
            font=('Segoe UI', 28, 'bold')
        ).pack(anchor='w', pady=(10, 0))
        
        # Trend
        if stat.get('trend'):
            trend_positive = stat.get('trend_positive', True)
            trend_icon = '↗' if trend_positive else '↘'
            trend_color = 'green' if trend_positive else 'red'
            
            ttk.Label(
                inner,
                text=f"{trend_icon} {stat['trend']}",
                font=('Segoe UI', 10),
                foreground=trend_color
            ).pack(anchor='w')
        
        return card
