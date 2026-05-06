"""
SRMS - Advanced Dashboard Widgets
Interactive widgets for dashboards with charts and analytics
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

try:
    import ttkbootstrap as ttk
    from ttkbootstrap.constants import *
    HAS_TTKBOOTSTRAP = True
except ImportError:
    HAS_TTKBOOTSTRAP = False


class ActivityTracker(ttk.Frame):
    """Real-time activity tracking widget."""
    
    def __init__(self, parent, user_id: int):
        super().__init__(parent)
        self.user_id = user_id
        self.activities = []
        
        self._create_widgets()
        self._start_tracking()
    
    def _create_widgets(self):
        """Create activity tracker widgets."""
        header = ttk.Frame(self)
        header.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(header, text="📊 Live Activity", font=('Segoe UI', 12, 'bold')).pack(side=tk.LEFT)
        
        self.status_var = tk.StringVar(value="● Online")
        status_label = ttk.Label(header, textvariable=self.status_var,
                                  foreground='green', font=('Segoe UI', 10))
        status_label.pack(side=tk.RIGHT)
        
        # Activity list
        self.activity_list = ttk.Treeview(self, columns=('Time', 'Action'), show='headings', height=8)
        self.activity_list.heading('Time', text='Time')
        self.activity_list.heading('Action', text='Action')
        self.activity_list.column('Time', width=80)
        self.activity_list.column('Action', width=200)
        self.activity_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def _start_tracking(self):
        """Start activity tracking."""
        self.log_activity("Session started")
        self._update_status()
    
    def _update_status(self):
        """Update online status."""
        current_time = datetime.now().strftime('%H:%M:%S')
        self.status_var.set(f"● Online ({current_time})")
        self.after(5000, self._update_status)
    
    def log_activity(self, action: str):
        """Log a user activity."""
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.activities.append({'time': timestamp, 'action': action})
        self.activity_list.insert('', 0, values=(timestamp, action))
        
        # Keep only last 50 activities
        children = self.activity_list.get_children()
        if len(children) > 50:
            self.activity_list.delete(children[-1])


class QuickStats(ttk.Frame):
    """Quick statistics widget with animated counters."""
    
    def __init__(self, parent, title: str, stats: list):
        """
        Args:
            stats: List of {'label': str, 'value': int, 'icon': str}
        """
        super().__init__(parent)
        self.stats = stats
        self._create_widgets(title)
    
    def _create_widgets(self, title):
        """Create stats widgets."""
        ttk.Label(self, text=title, font=('Segoe UI', 12, 'bold')).pack(pady=5)
        
        stats_frame = ttk.Frame(self)
        stats_frame.pack(fill=tk.X, padx=10, pady=5)
        
        for i, stat in enumerate(self.stats):
            if HAS_TTKBOOTSTRAP:
                card = ttk.Frame(stats_frame, bootstyle="dark")
            else:
                card = ttk.Frame(stats_frame, relief='raised', borderwidth=1)
            card.grid(row=0, column=i, padx=5, pady=5, sticky='nsew')
            stats_frame.columnconfigure(i, weight=1)
            
            ttk.Label(card, text=stat.get('icon', '📊'), font=('Segoe UI', 18)).pack(pady=(10, 0))
            ttk.Label(card, text=str(stat.get('value', 0)), font=('Segoe UI', 20, 'bold')).pack()
            ttk.Label(card, text=stat.get('label', ''), font=('Segoe UI', 9)).pack(pady=(0, 10))


class ProgressWidget(ttk.Frame):
    """Progress indicator widget."""
    
    def __init__(self, parent, title: str, items: list):
        """
        Args:
            items: List of {'label': str, 'current': int, 'total': int}
        """
        super().__init__(parent)
        self.items = items
        self._create_widgets(title)
    
    def _create_widgets(self, title):
        """Create progress widgets."""
        ttk.Label(self, text=title, font=('Segoe UI', 12, 'bold')).pack(pady=5, anchor='w')
        
        for item in self.items:
            frame = ttk.Frame(self)
            frame.pack(fill=tk.X, padx=10, pady=3)
            
            ttk.Label(frame, text=item['label'], width=20).pack(side=tk.LEFT)
            
            current = item.get('current', 0)
            total = item.get('total', 100)
            percentage = (current / total * 100) if total > 0 else 0
            
            if HAS_TTKBOOTSTRAP:
                progress = ttk.Progressbar(frame, length=150, value=percentage, bootstyle="success-striped")
            else:
                progress = ttk.Progressbar(frame, length=150, value=percentage)
            progress.pack(side=tk.LEFT, padx=10)
            
            ttk.Label(frame, text=f"{percentage:.0f}%").pack(side=tk.LEFT)


class CalendarWidget(ttk.Frame):
    """Simple calendar widget."""
    
    def __init__(self, parent, on_date_select=None):
        super().__init__(parent)
        self.on_date_select = on_date_select
        self.current_date = datetime.now()
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create calendar widgets."""
        # Header with month/year and navigation
        header = ttk.Frame(self)
        header.pack(fill=tk.X, pady=5)
        
        if HAS_TTKBOOTSTRAP:
            ttk.Button(header, text="◀", width=3, command=self._prev_month, bootstyle="outline").pack(side=tk.LEFT)
        else:
            ttk.Button(header, text="<", width=2, command=self._prev_month).pack(side=tk.LEFT)
        
        self.month_label = ttk.Label(header, font=('Segoe UI', 11, 'bold'))
        self.month_label.pack(side=tk.LEFT, expand=True)
        
        if HAS_TTKBOOTSTRAP:
            ttk.Button(header, text="▶", width=3, command=self._next_month, bootstyle="outline").pack(side=tk.RIGHT)
        else:
            ttk.Button(header, text=">", width=2, command=self._next_month).pack(side=tk.RIGHT)
        
        # Day headers
        days_frame = ttk.Frame(self)
        days_frame.pack(fill=tk.X)
        
        for day in ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa']:
            ttk.Label(days_frame, text=day, width=4, font=('Segoe UI', 9, 'bold')).pack(side=tk.LEFT, padx=1)
        
        # Calendar grid
        self.calendar_frame = ttk.Frame(self)
        self.calendar_frame.pack(fill=tk.BOTH, expand=True)
        
        self._update_calendar()
    
    def _update_calendar(self):
        """Update calendar display."""
        # Clear existing
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()
        
        # Update label
        self.month_label.config(text=self.current_date.strftime('%B %Y'))
        
        # Get first day of month and number of days
        import calendar
        cal = calendar.Calendar(6)  # Sunday start
        month_days = cal.monthdayscalendar(self.current_date.year, self.current_date.month)
        
        today = datetime.now()
        
        for week_num, week in enumerate(month_days):
            week_frame = ttk.Frame(self.calendar_frame)
            week_frame.pack(fill=tk.X)
            
            for day in week:
                if day == 0:
                    ttk.Label(week_frame, text="", width=4).pack(side=tk.LEFT, padx=1)
                else:
                    is_today = (day == today.day and 
                               self.current_date.month == today.month and
                               self.current_date.year == today.year)
                    
                    if HAS_TTKBOOTSTRAP:
                        style = "primary" if is_today else "secondary-outline"
                        btn = ttk.Button(week_frame, text=str(day), width=3,
                                         command=lambda d=day: self._select_date(d),
                                         bootstyle=style)
                    else:
                        btn = ttk.Button(week_frame, text=str(day), width=3,
                                         command=lambda d=day: self._select_date(d))
                    btn.pack(side=tk.LEFT, padx=1, pady=1)
    
    def _prev_month(self):
        """Go to previous month."""
        self.current_date = self.current_date.replace(day=1) - timedelta(days=1)
        self._update_calendar()
    
    def _next_month(self):
        """Go to next month."""
        next_month = self.current_date.replace(day=28) + timedelta(days=4)
        self.current_date = next_month.replace(day=1)
        self._update_calendar()
    
    def _select_date(self, day: int):
        """Handle date selection."""
        selected = self.current_date.replace(day=day)
        if self.on_date_select:
            self.on_date_select(selected)


class DataVisualization(ttk.Frame):
    """Data visualization widget with various chart types."""
    
    def __init__(self, parent, width: int = 400, height: int = 250):
        super().__init__(parent)
        self.chart_width = width
        self.chart_height = height
        
        self.canvas = tk.Canvas(self, width=width, height=height, bg='white')
        self.canvas.pack(fill=tk.BOTH, expand=True)
    
    def draw_bar_chart(self, data: dict, title: str = "Bar Chart", colors: list = None):
        """
        Draw a bar chart.
        
        Args:
            data: {'label': value, ...}
        """
        self.canvas.delete('all')
        
        if not data:
            return
        
        default_colors = ['#4CAF50', '#2196F3', '#FF9800', '#E91E63', '#9C27B0']
        colors = colors or default_colors
        
        # Title
        self.canvas.create_text(
            self.chart_width // 2, 20,
            text=title, font=('Segoe UI', 12, 'bold')
        )
        
        # Calculate bar dimensions
        margin = 50
        chart_width = self.chart_width - 2 * margin
        chart_height = self.chart_height - 80
        
        n_bars = len(data)
        bar_width = chart_width // n_bars - 10
        max_value = max(data.values()) if data.values() else 1
        
        # Draw bars
        x = margin + 5
        for i, (label, value) in enumerate(data.items()):
            bar_height = (value / max_value) * chart_height
            y = self.chart_height - 40
            
            color = colors[i % len(colors)]
            
            # Bar
            self.canvas.create_rectangle(
                x, y - bar_height, x + bar_width, y,
                fill=color, outline=''
            )
            
            # Value label
            self.canvas.create_text(
                x + bar_width // 2, y - bar_height - 10,
                text=str(value), font=('Segoe UI', 9)
            )
            
            # X-axis label
            self.canvas.create_text(
                x + bar_width // 2, y + 15,
                text=label[:8], font=('Segoe UI', 9), angle=0
            )
            
            x += bar_width + 10
    
    def draw_pie_chart(self, data: dict, title: str = "Pie Chart", colors: list = None):
        """
        Draw a pie chart.
        
        Args:
            data: {'label': value, ...}
        """
        self.canvas.delete('all')
        
        if not data:
            return
        
        default_colors = ['#4CAF50', '#2196F3', '#FF9800', '#E91E63', '#9C27B0', '#00BCD4']
        colors = colors or default_colors
        
        # Title
        self.canvas.create_text(
            self.chart_width // 2, 20,
            text=title, font=('Segoe UI', 12, 'bold')
        )
        
        # Calculate pie dimensions
        total = sum(data.values())
        if total == 0:
            return
        
        cx = self.chart_width // 2 - 50
        cy = self.chart_height // 2 + 10
        radius = min(self.chart_width, self.chart_height) // 3
        
        # Draw slices
        start_angle = 0
        for i, (label, value) in enumerate(data.items()):
            extent = (value / total) * 360
            color = colors[i % len(colors)]
            
            self.canvas.create_arc(
                cx - radius, cy - radius, cx + radius, cy + radius,
                start=start_angle, extent=extent,
                fill=color, outline='white', width=2
            )
            
            start_angle += extent
        
        # Legend
        legend_x = self.chart_width - 100
        legend_y = 50
        
        for i, (label, value) in enumerate(data.items()):
            color = colors[i % len(colors)]
            percentage = (value / total * 100)
            
            self.canvas.create_rectangle(
                legend_x, legend_y, legend_x + 15, legend_y + 15,
                fill=color, outline=''
            )
            self.canvas.create_text(
                legend_x + 20, legend_y + 7,
                text=f"{label}: {percentage:.1f}%",
                anchor='w', font=('Segoe UI', 8)
            )
            
            legend_y += 20
    
    def draw_line_chart(self, data: list, title: str = "Line Chart", color: str = '#2196F3'):
        """
        Draw a line chart.
        
        Args:
            data: List of (x_label, y_value) tuples
        """
        self.canvas.delete('all')
        
        if not data:
            return
        
        # Title
        self.canvas.create_text(
            self.chart_width // 2, 20,
            text=title, font=('Segoe UI', 12, 'bold')
        )
        
        # Calculate dimensions
        margin = 50
        chart_width = self.chart_width - 2 * margin
        chart_height = self.chart_height - 80
        
        max_value = max(d[1] for d in data) if data else 1
        n_points = len(data)
        
        # Draw axes
        self.canvas.create_line(margin, self.chart_height - 40, 
                                self.chart_width - margin, self.chart_height - 40,
                                fill='gray')
        self.canvas.create_line(margin, 40, margin, self.chart_height - 40, fill='gray')
        
        # Draw line and points
        points = []
        x_step = chart_width / (n_points - 1) if n_points > 1 else chart_width
        
        for i, (label, value) in enumerate(data):
            x = margin + i * x_step
            y = self.chart_height - 40 - (value / max_value) * chart_height
            points.extend([x, y])
            
            # Point
            self.canvas.create_oval(x - 4, y - 4, x + 4, y + 4, fill=color, outline='white')
            
            # X label
            if i % 2 == 0:  # Every other label
                self.canvas.create_text(x, self.chart_height - 25, text=label[:6], 
                                        font=('Segoe UI', 8))
        
        # Draw line
        if len(points) >= 4:
            self.canvas.create_line(points, fill=color, width=2, smooth=True)


class HelpWidget(ttk.Frame):
    """Contextual help widget."""
    
    HELP_TOPICS = {
        'security': {
            'title': '🔒 Security Features',
            'content': '''
• RBAC: Role-Based Access Control
• MLS: Multilevel Security (Bell-LaPadula)
• Encryption: AES-256 for sensitive data
• 2FA: Two-Factor Authentication
• Password Hashing: bcrypt with salt
            '''
        },
        'roles': {
            'title': '👥 User Roles',
            'content': '''
• Admin (4): Full system access
• Instructor (3): Grades management
• TA (2): Attendance management
• Student (1): Own data only
• Guest (0): Public info only
            '''
        },
        'grades': {
            'title': '📊 Grades',
            'content': '''
• Only Instructors can enter grades
• Grades are encrypted in database
• Students see only published grades
• GPA calculated automatically
            '''
        },
        'shortcuts': {
            'title': '⌨️ Keyboard Shortcuts',
            'content': '''
• Ctrl+R: Refresh data
• Ctrl+S: Save changes
• Ctrl+P: Print (if allowed)
• Ctrl+E: Export (if allowed)
• F5: Full refresh
• Esc: Close dialog
            '''
        }
    }
    
    def __init__(self, parent, topic: str = 'security'):
        super().__init__(parent)
        self.topic = topic
        self._create_widgets()
    
    def _create_widgets(self):
        """Create help widgets."""
        help_data = self.HELP_TOPICS.get(self.topic, self.HELP_TOPICS['security'])
        
        ttk.Label(self, text=help_data['title'], font=('Segoe UI', 12, 'bold')).pack(pady=5)
        
        text = tk.Text(self, wrap=tk.WORD, height=10, width=40, font=('Segoe UI', 10))
        text.insert('1.0', help_data['content'])
        text.config(state='disabled')
        text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)


class QuickActions(ttk.Frame):
    """Quick action buttons panel."""
    
    def __init__(self, parent, actions: list):
        """
        Args:
            actions: List of {'label': str, 'icon': str, 'command': callable}
        """
        super().__init__(parent)
        self.actions = actions
        self._create_widgets()
    
    def _create_widgets(self):
        """Create action buttons."""
        ttk.Label(self, text="⚡ Quick Actions", font=('Segoe UI', 11, 'bold')).pack(pady=5)
        
        for action in self.actions:
            if HAS_TTKBOOTSTRAP:
                btn = ttk.Button(
                    self,
                    text=f"{action.get('icon', '')} {action['label']}",
                    command=action.get('command', lambda: None),
                    bootstyle="outline",
                    width=25
                )
            else:
                btn = ttk.Button(
                    self,
                    text=action['label'],
                    command=action.get('command', lambda: None),
                    width=25
                )
            btn.pack(pady=2, padx=5)


class Breadcrumb(ttk.Frame):
    """Navigation breadcrumb."""
    
    def __init__(self, parent, path: list, on_navigate=None):
        """
        Args:
            path: List of {'label': str, 'id': any}
        """
        super().__init__(parent)
        self.path = path
        self.on_navigate = on_navigate
        self._create_widgets()
    
    def _create_widgets(self):
        """Create breadcrumb widgets."""
        for i, item in enumerate(self.path):
            if i > 0:
                ttk.Label(self, text=" › ", font=('Segoe UI', 10)).pack(side=tk.LEFT)
            
            if i < len(self.path) - 1:
                # Clickable
                btn = ttk.Button(
                    self, text=item['label'],
                    command=lambda id=item.get('id'): self._navigate(id)
                )
                btn.pack(side=tk.LEFT)
            else:
                # Current (not clickable)
                ttk.Label(self, text=item['label'], font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT)
    
    def _navigate(self, id):
        """Handle navigation."""
        if self.on_navigate:
            self.on_navigate(id)
