"""
SRMS - Enhanced Student Features
Student-specific features including GPA viewer, transcript, enrollment
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

try:
    import ttkbootstrap as ttk
    from ttkbootstrap.constants import *
    HAS_TTKBOOTSTRAP = True
except ImportError:
    HAS_TTKBOOTSTRAP = False

from src.database.connection import get_database


class GPAViewer(ttk.Frame):
    """Student GPA and academic standing viewer."""
    
    def __init__(self, parent, student_id: int):
        super().__init__(parent)
        self.student_id = student_id
        self.db = get_database()
        
        self._create_widgets()
        self._load_data()
    
    def _create_widgets(self):
        """Create GPA viewer widgets."""
        # Header
        ttk.Label(self, text="📊 Academic Standing", font=('Segoe UI', 16, 'bold')).pack(pady=10)
        
        # GPA Card
        gpa_card = ttk.Frame(self)
        gpa_card.pack(fill=tk.X, padx=20, pady=10)
        
        self.gpa_label = ttk.Label(gpa_card, text="0.00", font=('Segoe UI', 48, 'bold'))
        self.gpa_label.pack()
        
        ttk.Label(gpa_card, text="Cumulative GPA", font=('Segoe UI', 12)).pack()
        
        self.standing_label = ttk.Label(gpa_card, text="", font=('Segoe UI', 11))
        self.standing_label.pack(pady=5)
        
        # Stats
        stats_frame = ttk.Frame(self)
        stats_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.stats = {}
        for i, (key, label) in enumerate([('credits', 'Credits'), ('courses', 'Courses'), ('a_grades', 'A Grades')]):
            frame = ttk.Frame(stats_frame)
            frame.grid(row=0, column=i, padx=20, pady=10)
            stats_frame.columnconfigure(i, weight=1)
            
            self.stats[key] = ttk.Label(frame, text="0", font=('Segoe UI', 24, 'bold'))
            self.stats[key].pack()
            ttk.Label(frame, text=label).pack()
        
        # Grade distribution
        dist_frame = ttk.Labelframe(self, text="Grade Distribution")
        dist_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.dist_canvas = tk.Canvas(dist_frame, height=120, bg='white')
        self.dist_canvas.pack(fill=tk.X, padx=10, pady=10)
    
    def _load_data(self):
        """Load GPA and grades data."""
        from src.security.advanced_security import GPACalculator
        
        # Get grades
        grades = self.db.fetch_all("""
            SELECT g.grade_letter, c.course_name FROM GRADES g
            JOIN COURSE c ON g.course_id = c.course_id
            WHERE g.student_id = ? AND g.is_published = 1
        """, (self.student_id,))
        
        if not grades:
            self.gpa_label.config(text="N/A")
            self.standing_label.config(text="No grades available")
            return
        
        # Calculate GPA
        grade_list = [{'letter': g['grade_letter'], 'credits': 3} for g in grades]
        result = GPACalculator.calculate_gpa(grade_list)
        
        self.gpa_label.config(text=f"{result['gpa']:.2f}")
        self.standing_label.config(text=GPACalculator.get_gpa_classification(result['gpa']))
        
        # Stats
        self.stats['credits'].config(text=str(result['total_credits']))
        self.stats['courses'].config(text=str(len(grades)))
        
        # Count A grades
        a_count = sum(1 for g in grades if g['grade_letter'].startswith('A'))
        self.stats['a_grades'].config(text=str(a_count))
        
        # Draw distribution
        self._draw_distribution(grades)
    
    def _draw_distribution(self, grades):
        """Draw grade distribution chart."""
        self.dist_canvas.delete('all')
        
        # Count grades
        counts = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}
        for g in grades:
            letter = g['grade_letter'][0] if g['grade_letter'] else 'F'
            if letter in counts:
                counts[letter] += 1
        
        colors = {'A': '#28a745', 'B': '#17a2b8', 'C': '#ffc107', 'D': '#fd7e14', 'F': '#dc3545'}
        max_count = max(counts.values()) if any(counts.values()) else 1
        
        x = 30
        bar_width = 50
        for letter, count in counts.items():
            height = (count / max_count) * 80 if max_count > 0 else 0
            y = 100
            
            self.dist_canvas.create_rectangle(x, y - height, x + bar_width, y,
                                               fill=colors[letter], outline='')
            self.dist_canvas.create_text(x + bar_width // 2, y + 10, text=letter)
            self.dist_canvas.create_text(x + bar_width // 2, y - height - 10, text=str(count))
            
            x += bar_width + 20


class TranscriptViewer(ttk.Frame):
    """Student transcript viewer with export."""
    
    def __init__(self, parent, student_id: int):
        super().__init__(parent)
        self.student_id = student_id
        self.db = get_database()
        
        self._create_widgets()
        self._load_transcript()
    
    def _create_widgets(self):
        """Create transcript widgets."""
        # Header
        header = ttk.Frame(self)
        header.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(header, text="📜 Academic Transcript", font=('Segoe UI', 16, 'bold')).pack(side=tk.LEFT)
        
        if HAS_TTKBOOTSTRAP:
            ttk.Button(header, text="📥 Export", command=self._export_transcript,
                       bootstyle="success-outline").pack(side=tk.RIGHT)
            ttk.Button(header, text="🖨 Print", command=self._print_transcript,
                       bootstyle="info-outline").pack(side=tk.RIGHT, padx=5)
        else:
            ttk.Button(header, text="Export", command=self._export_transcript).pack(side=tk.RIGHT)
            ttk.Button(header, text="Print", command=self._print_transcript).pack(side=tk.RIGHT, padx=5)
        
        # Student info
        self.info_frame = ttk.Labelframe(self, text="Student Information")
        self.info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Grades table
        grades_frame = ttk.Labelframe(self, text="Academic Record")
        grades_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        cols = ('Course', 'Name', 'Grade', 'Credits')
        self.grades_tree = ttk.Treeview(grades_frame, columns=cols, show='headings', height=10)
        for col in cols:
            self.grades_tree.heading(col, text=col)
            self.grades_tree.column(col, width=120)
        self.grades_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Summary
        self.summary_frame = ttk.Frame(self)
        self.summary_frame.pack(fill=tk.X, padx=10, pady=10)
    
    def _load_transcript(self):
        """Load transcript data."""
        from src.security.advanced_security import TranscriptGenerator
        
        tg = TranscriptGenerator()
        transcript = tg.generate_transcript(self.student_id)
        
        if not transcript:
            ttk.Label(self.info_frame, text="Transcript not available").pack()
            return
        
        # Student info
        for widget in self.info_frame.winfo_children():
            widget.destroy()
        
        info = ttk.Frame(self.info_frame)
        info.pack(fill=tk.X, padx=10, pady=5)
        
        student = transcript['student']
        ttk.Label(info, text=f"Name: {student['full_name']}", font=('Segoe UI', 11)).grid(row=0, column=0, sticky='w')
        ttk.Label(info, text=f"Department: {student.get('department', 'N/A')}", font=('Segoe UI', 11)).grid(row=0, column=1, sticky='w', padx=20)
        ttk.Label(info, text=f"Generated: {datetime.now().strftime('%Y-%m-%d')}", font=('Segoe UI', 11)).grid(row=0, column=2, sticky='w', padx=20)
        
        # Grades
        for item in self.grades_tree.get_children():
            self.grades_tree.delete(item)
        
        for grade in transcript['grades']:
            self.grades_tree.insert('', 'end', values=(
                grade['course_code'],
                grade['course_name'],
                grade['grade_letter'],
                3  # Default credits
            ))
        
        # Summary
        for widget in self.summary_frame.winfo_children():
            widget.destroy()
        
        gpa = transcript['gpa']
        ttk.Label(self.summary_frame, text=f"Cumulative GPA: {gpa['gpa']:.2f}",
                  font=('Segoe UI', 12, 'bold')).pack(side=tk.LEFT, padx=10)
        ttk.Label(self.summary_frame, text=f"Total Credits: {gpa['total_credits']}",
                  font=('Segoe UI', 12)).pack(side=tk.LEFT, padx=10)
        ttk.Label(self.summary_frame, text=f"Standing: {transcript['classification']}",
                  font=('Segoe UI', 12)).pack(side=tk.LEFT, padx=10)
    
    def _export_transcript(self):
        """Export transcript to file."""
        from src.security.advanced_security import TranscriptGenerator
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            tg = TranscriptGenerator()
            text = tg.export_transcript_text(self.student_id)
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(text)
            
            messagebox.showinfo("Success", f"Transcript exported to {filename}")
    
    def _print_transcript(self):
        """Print transcript (show preview)."""
        from src.security.advanced_security import TranscriptGenerator
        
        tg = TranscriptGenerator()
        text = tg.export_transcript_text(self.student_id)
        
        # Show in popup
        popup = tk.Toplevel(self)
        popup.title("Print Preview")
        popup.geometry("500x600")
        
        text_widget = tk.Text(popup, wrap=tk.WORD, font=('Consolas', 10))
        text_widget.insert('1.0', text)
        text_widget.config(state='disabled')
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        if HAS_TTKBOOTSTRAP:
            ttk.Button(popup, text="Close", command=popup.destroy, bootstyle="secondary").pack(pady=10)
        else:
            ttk.Button(popup, text="Close", command=popup.destroy).pack(pady=10)


class CourseEnrollmentManager(ttk.Frame):
    """Student course enrollment manager."""
    
    def __init__(self, parent, student_id: int, user_id: int):
        super().__init__(parent)
        self.student_id = student_id
        self.user_id = user_id
        self.db = get_database()
        
        self._create_widgets()
        self._load_data()
    
    def _create_widgets(self):
        """Create enrollment widgets."""
        # Current enrollments
        enrolled_frame = ttk.Labelframe(self, text="📚 My Courses")
        enrolled_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        cols = ('Course', 'Name', 'Instructor', 'Status')
        self.enrolled_tree = ttk.Treeview(enrolled_frame, columns=cols, show='headings', height=6)
        for col in cols:
            self.enrolled_tree.heading(col, text=col)
            self.enrolled_tree.column(col, width=120)
        self.enrolled_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Available courses
        available_frame = ttk.Labelframe(self, text="📋 Available Courses")
        available_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Filter
        filter_frame = ttk.Frame(available_frame)
        filter_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(filter_frame, text="Search:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self._filter_courses())
        ttk.Entry(filter_frame, textvariable=self.search_var, width=30).pack(side=tk.LEFT, padx=5)
        
        if HAS_TTKBOOTSTRAP:
            ttk.Button(filter_frame, text="✚ Enroll", command=self._enroll_course,
                       bootstyle="success").pack(side=tk.RIGHT)
        else:
            ttk.Button(filter_frame, text="Enroll", command=self._enroll_course).pack(side=tk.RIGHT)
        
        cols = ('Code', 'Name', 'Description', 'Instructor')
        self.available_tree = ttk.Treeview(available_frame, columns=cols, show='headings', height=6)
        for col in cols:
            self.available_tree.heading(col, text=col)
            self.available_tree.column(col, width=120)
        self.available_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def _load_data(self):
        """Load enrollment data."""
        # Load enrolled courses
        enrolled = self.db.fetch_all("""
            SELECT e.*, c.course_code, c.course_name, i.full_name as instructor_name
            FROM ENROLLMENT e
            JOIN COURSE c ON e.course_id = c.course_id
            LEFT JOIN INSTRUCTOR i ON c.instructor_id = i.instructor_id
            WHERE e.student_id = ?
        """, (self.student_id,))
        
        for item in self.enrolled_tree.get_children():
            self.enrolled_tree.delete(item)
        
        for e in enrolled:
            self.enrolled_tree.insert('', 'end', values=(
                e['course_code'],
                e['course_name'],
                e.get('instructor_name', 'TBA'),
                e.get('status', 'active').title()
            ))
        
        # Load available courses
        self._load_available_courses()
    
    def _load_available_courses(self):
        """Load available courses."""
        courses = self.db.fetch_all("""
            SELECT c.*, i.full_name as instructor_name FROM COURSE c
            LEFT JOIN INSTRUCTOR i ON c.instructor_id = i.instructor_id
            WHERE c.course_id NOT IN (SELECT course_id FROM ENROLLMENT WHERE student_id = ?)
        """, (self.student_id,))
        
        self.all_courses = courses  # Store for filtering
        self._display_courses(courses)
    
    def _display_courses(self, courses):
        """Display courses in tree."""
        for item in self.available_tree.get_children():
            self.available_tree.delete(item)
        
        for c in courses:
            self.available_tree.insert('', 'end', values=(
                c['course_code'],
                c['course_name'],
                c.get('description', '')[:50] + '...' if c.get('description', '') else '',
                c.get('instructor_name', 'TBA')
            ), iid=str(c['course_id']))
    
    def _filter_courses(self):
        """Filter courses by search."""
        query = self.search_var.get().lower()
        if not query:
            self._display_courses(self.all_courses)
        else:
            filtered = [c for c in self.all_courses if 
                       query in c['course_code'].lower() or
                       query in c['course_name'].lower()]
            self._display_courses(filtered)
    
    def _enroll_course(self):
        """Enroll in selected course."""
        selected = self.available_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a course")
            return
        
        course_id = int(selected[0])
        
        try:
            self.db.execute("""
                INSERT INTO ENROLLMENT (student_id, course_id, status)
                VALUES (?, ?, 'active')
            """, (self.student_id, course_id))
            self.db.commit()
            
            messagebox.showinfo("Success", "Successfully enrolled in course!")
            self._load_data()
        except Exception as e:
            messagebox.showerror("Error", f"Enrollment failed: {e}")


class AttendanceViewer(ttk.Frame):
    """Student attendance viewer with statistics."""
    
    def __init__(self, parent, student_id: int):
        super().__init__(parent)
        self.student_id = student_id
        self.db = get_database()
        
        self._create_widgets()
        self._load_data()
    
    def _create_widgets(self):
        """Create attendance widgets."""
        # Header
        header = ttk.Frame(self)
        header.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(header, text="📅 Attendance Record", font=('Segoe UI', 16, 'bold')).pack(side=tk.LEFT)
        
        if HAS_TTKBOOTSTRAP:
            ttk.Button(header, text="🔄 Refresh", command=self._load_data,
                       bootstyle="info-outline").pack(side=tk.RIGHT)
        else:
            ttk.Button(header, text="Refresh", command=self._load_data).pack(side=tk.RIGHT)
        
        # Summary cards
        summary_frame = ttk.Frame(self)
        summary_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.summary_labels = {}
        for i, (key, label, color) in enumerate([
            ('present', 'Present', '#28a745'),
            ('absent', 'Absent', '#dc3545'),
            ('late', 'Late', '#ffc107'),
            ('excused', 'Excused', '#17a2b8')
        ]):
            frame = ttk.Frame(summary_frame)
            frame.grid(row=0, column=i, padx=10, pady=5, sticky='nsew')
            summary_frame.columnconfigure(i, weight=1)
            
            self.summary_labels[key] = ttk.Label(frame, text="0", font=('Segoe UI', 28, 'bold'))
            self.summary_labels[key].pack()
            ttk.Label(frame, text=label).pack()
        
        # Attendance rate
        rate_frame = ttk.Frame(self)
        rate_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(rate_frame, text="Overall Attendance Rate:").pack(side=tk.LEFT)
        self.rate_label = ttk.Label(rate_frame, text="0%", font=('Segoe UI', 12, 'bold'))
        self.rate_label.pack(side=tk.LEFT, padx=10)
        
        if HAS_TTKBOOTSTRAP:
            self.rate_bar = ttk.Progressbar(rate_frame, length=200, bootstyle="success-striped")
        else:
            self.rate_bar = ttk.Progressbar(rate_frame, length=200)
        self.rate_bar.pack(side=tk.LEFT)
        
        # Attendance table
        table_frame = ttk.Labelframe(self, text="Detailed Records")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        cols = ('Date', 'Course', 'Status')
        self.tree = ttk.Treeview(table_frame, columns=cols, show='headings', height=10)
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def _load_data(self):
        """Load attendance data."""
        # Get attendance records
        records = self.db.fetch_all("""
            SELECT a.*, c.course_code, c.course_name FROM ATTENDANCE a
            JOIN COURSE c ON a.course_id = c.course_id
            WHERE a.student_id = ?
            ORDER BY a.attendance_date DESC
        """, (self.student_id,))
        
        # Calculate summary
        counts = {'Present': 0, 'Absent': 0, 'Late': 0, 'Excused': 0}
        for r in records:
            if r['status'] in counts:
                counts[r['status']] += 1
        
        self.summary_labels['present'].config(text=str(counts['Present']))
        self.summary_labels['absent'].config(text=str(counts['Absent']))
        self.summary_labels['late'].config(text=str(counts['Late']))
        self.summary_labels['excused'].config(text=str(counts['Excused']))
        
        # Calculate rate
        total = sum(counts.values())
        rate = (counts['Present'] + counts['Late']) / total * 100 if total > 0 else 0
        self.rate_label.config(text=f"{rate:.1f}%")
        self.rate_bar['value'] = rate
        
        # Populate table
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for r in records:
            self.tree.insert('', 'end', values=(
                r['attendance_date'],
                f"{r['course_code']} - {r['course_name']}",
                r['status']
            ))


class NotificationCenter(ttk.Frame):
    """Student notification center."""
    
    def __init__(self, parent, user_id: int):
        super().__init__(parent)
        self.user_id = user_id
        self.db = get_database()
        
        self._create_widgets()
        self._load_notifications()
    
    def _create_widgets(self):
        """Create notification widgets."""
        # Header
        header = ttk.Frame(self)
        header.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(header, text="🔔 Notifications", font=('Segoe UI', 16, 'bold')).pack(side=tk.LEFT)
        
        btn_frame = ttk.Frame(header)
        btn_frame.pack(side=tk.RIGHT)
        
        if HAS_TTKBOOTSTRAP:
            ttk.Button(btn_frame, text="✓ Mark All Read", command=self._mark_all_read,
                       bootstyle="success-outline").pack(side=tk.LEFT, padx=5)
            ttk.Button(btn_frame, text="🔄 Refresh", command=self._load_notifications,
                       bootstyle="info-outline").pack(side=tk.LEFT)
        else:
            ttk.Button(btn_frame, text="Mark All Read", command=self._mark_all_read).pack(side=tk.LEFT, padx=5)
            ttk.Button(btn_frame, text="Refresh", command=self._load_notifications).pack(side=tk.LEFT)
        
        # Notifications list
        self.notifications_frame = ttk.Frame(self)
        self.notifications_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
    def _load_notifications(self):
        """Load notifications."""
        for widget in self.notifications_frame.winfo_children():
            widget.destroy()
        
        notifications = self.db.fetch_all("""
            SELECT * FROM NOTIFICATIONS WHERE user_id = ?
            ORDER BY created_at DESC LIMIT 20
        """, (self.user_id,))
        
        if not notifications:
            ttk.Label(self.notifications_frame, text="No notifications",
                      font=('Segoe UI', 12)).pack(pady=20)
            return
        
        for notif in notifications:
            self._create_notification_card(notif)
    
    def _create_notification_card(self, notif: dict):
        """Create notification card."""
        is_read = notif.get('is_read', 0)
        
        if HAS_TTKBOOTSTRAP:
            style = "secondary" if is_read else "info"
            card = ttk.Frame(self.notifications_frame, bootstyle=style)
        else:
            card = ttk.Frame(self.notifications_frame, relief='raised', borderwidth=1)
        card.pack(fill=tk.X, pady=3)
        
        # Icon
        type_icons = {'info': 'ℹ️', 'success': '✅', 'warning': '⚠️', 'error': '❌'}
        icon = type_icons.get(notif.get('notification_type', 'info'), 'ℹ️')
        
        ttk.Label(card, text=icon, font=('Segoe UI', 16)).pack(side=tk.LEFT, padx=10, pady=5)
        
        # Content
        content = ttk.Frame(card)
        content.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=5)
        
        ttk.Label(content, text=notif['title'], font=('Segoe UI', 11, 'bold')).pack(anchor='w')
        ttk.Label(content, text=notif['message'], font=('Segoe UI', 10)).pack(anchor='w')
        
        created = notif.get('created_at', '')[:16] if notif.get('created_at') else ''
        ttk.Label(content, text=created, font=('Segoe UI', 9)).pack(anchor='w')
        
        # Mark as read button
        if not is_read:
            if HAS_TTKBOOTSTRAP:
                ttk.Button(card, text="✓", width=3, command=lambda n=notif: self._mark_read(n),
                           bootstyle="success-outline").pack(side=tk.RIGHT, padx=10)
            else:
                ttk.Button(card, text="✓", width=3, command=lambda n=notif: self._mark_read(n)).pack(side=tk.RIGHT, padx=10)
    
    def _mark_read(self, notif: dict):
        """Mark notification as read."""
        self.db.execute("""
            UPDATE NOTIFICATIONS SET is_read = 1, read_at = ?
            WHERE notification_id = ?
        """, (datetime.now(), notif['notification_id']))
        self.db.commit()
        self._load_notifications()
    
    def _mark_all_read(self):
        """Mark all notifications as read."""
        self.db.execute("""
            UPDATE NOTIFICATIONS SET is_read = 1, read_at = ?
            WHERE user_id = ? AND is_read = 0
        """, (datetime.now(), self.user_id))
        self.db.commit()
        self._load_notifications()
