"""
SRMS - Two-Factor Authentication (2FA) Simulation
Implements TOTP-style 2FA for enhanced security
"""

import sys
import os
import random
import string
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

try:
    import ttkbootstrap as ttk
    from ttkbootstrap.constants import *
    HAS_TTKBOOTSTRAP = True
except ImportError:
    HAS_TTKBOOTSTRAP = False


class TwoFactorAuth:
    """Two-Factor Authentication manager."""
    
    def __init__(self):
        self.pending_codes = {}  # user_id: {'code': str, 'expires': datetime}
        self.code_length = 6
        self.code_validity_seconds = 300  # 5 minutes
    
    def generate_code(self, user_id: int) -> str:
        """Generate a new 2FA code for user."""
        code = ''.join(random.choices(string.digits, k=self.code_length))
        expires = datetime.now() + timedelta(seconds=self.code_validity_seconds)
        
        self.pending_codes[user_id] = {
            'code': code,
            'expires': expires,
            'attempts': 0
        }
        
        return code
    
    def verify_code(self, user_id: int, entered_code: str) -> dict:
        """Verify 2FA code."""
        if user_id not in self.pending_codes:
            return {'valid': False, 'reason': 'No pending verification'}
        
        pending = self.pending_codes[user_id]
        
        # Check expiry
        if datetime.now() > pending['expires']:
            del self.pending_codes[user_id]
            return {'valid': False, 'reason': 'Code expired'}
        
        # Check attempts
        if pending['attempts'] >= 3:
            del self.pending_codes[user_id]
            return {'valid': False, 'reason': 'Too many attempts'}
        
        # Verify code
        if entered_code == pending['code']:
            del self.pending_codes[user_id]
            return {'valid': True, 'reason': 'Verification successful'}
        
        pending['attempts'] += 1
        return {'valid': False, 'reason': f'Invalid code ({3 - pending["attempts"]} attempts remaining)'}
    
    def get_remaining_time(self, user_id: int) -> int:
        """Get remaining seconds for code validity."""
        if user_id not in self.pending_codes:
            return 0
        
        remaining = (self.pending_codes[user_id]['expires'] - datetime.now()).total_seconds()
        return max(0, int(remaining))


class TwoFactorDialog:
    """2FA verification dialog."""
    
    def __init__(self, parent, user_id: int, tfa_manager: TwoFactorAuth):
        self.parent = parent
        self.user_id = user_id
        self.tfa = tfa_manager
        self.result = False
        
        # Generate code
        self.code = self.tfa.generate_code(user_id)
        
        self._create_dialog()
    
    def _create_dialog(self):
        """Create 2FA dialog."""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("🔐 Two-Factor Authentication")
        self.dialog.geometry("400x350")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        self.dialog.resizable(False, False)
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() - 400) // 2
        y = (self.dialog.winfo_screenheight() - 350) // 2
        self.dialog.geometry(f"+{x}+{y}")
        
        # Main frame
        main = ttk.Frame(self.dialog)
        main.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        # Icon and title
        ttk.Label(main, text="🔐", font=('Segoe UI', 48)).pack()
        ttk.Label(main, text="Verification Required", font=('Segoe UI', 16, 'bold')).pack(pady=5)
        
        # Simulated code display (in real app, this would be sent via email/SMS)
        code_frame = ttk.Labelframe(main, text="📧 Your Verification Code (Simulated)")
        code_frame.pack(fill=tk.X, pady=15)
        
        ttk.Label(code_frame, text=self.code, font=('Consolas', 24, 'bold'),
                  foreground='#28a745').pack(pady=10)
        ttk.Label(code_frame, text="(In production, this would be sent via email/SMS)",
                  font=('Segoe UI', 9)).pack(pady=(0, 5))
        
        # Code entry
        ttk.Label(main, text="Enter Verification Code:").pack(anchor='w', pady=(10, 5))
        
        self.code_var = tk.StringVar()
        self.code_entry = ttk.Entry(main, textvariable=self.code_var, font=('Consolas', 18),
                                     justify='center', width=10)
        self.code_entry.pack(pady=5)
        self.code_entry.focus()
        
        # Timer
        self.timer_var = tk.StringVar()
        self.timer_label = ttk.Label(main, textvariable=self.timer_var, font=('Segoe UI', 10))
        self.timer_label.pack(pady=5)
        self._update_timer()
        
        # Buttons
        btn_frame = ttk.Frame(main)
        btn_frame.pack(pady=15)
        
        if HAS_TTKBOOTSTRAP:
            ttk.Button(btn_frame, text="✓ Verify", command=self._verify,
                       bootstyle="success", width=12).pack(side=tk.LEFT, padx=5)
            ttk.Button(btn_frame, text="✗ Cancel", command=self._cancel,
                       bootstyle="danger-outline", width=12).pack(side=tk.LEFT, padx=5)
        else:
            ttk.Button(btn_frame, text="Verify", command=self._verify).pack(side=tk.LEFT, padx=5)
            ttk.Button(btn_frame, text="Cancel", command=self._cancel).pack(side=tk.LEFT, padx=5)
        
        # Bind Enter key
        self.dialog.bind('<Return>', lambda e: self._verify())
    
    def _update_timer(self):
        """Update countdown timer."""
        remaining = self.tfa.get_remaining_time(self.user_id)
        if remaining > 0:
            mins, secs = divmod(remaining, 60)
            self.timer_var.set(f"⏱ Code expires in: {mins}:{secs:02d}")
            self.dialog.after(1000, self._update_timer)
        else:
            self.timer_var.set("⚠️ Code expired!")
    
    def _verify(self):
        """Verify entered code."""
        result = self.tfa.verify_code(self.user_id, self.code_var.get())
        
        if result['valid']:
            self.result = True
            self.dialog.destroy()
        else:
            messagebox.showerror("Verification Failed", result['reason'])
            if 'expired' in result['reason'].lower() or 'attempts' in result['reason'].lower():
                self.dialog.destroy()
    
    def _cancel(self):
        """Cancel verification."""
        self.result = False
        self.dialog.destroy()
    
    def show(self) -> bool:
        """Show dialog and return result."""
        self.dialog.wait_window()
        return self.result


class SessionManager:
    """User session management with timeout."""
    
    def __init__(self, timeout_minutes: int = 30):
        self.timeout_minutes = timeout_minutes
        self.sessions = {}  # user_id: {'last_activity': datetime, 'data': dict}
    
    def create_session(self, user_id: int, user_data: dict) -> str:
        """Create new session."""
        import hashlib
        session_token = hashlib.sha256(
            f"{user_id}{datetime.now().isoformat()}{random.random()}".encode()
        ).hexdigest()[:32]
        
        self.sessions[user_id] = {
            'token': session_token,
            'last_activity': datetime.now(),
            'data': user_data,
            'created': datetime.now()
        }
        
        return session_token
    
    def validate_session(self, user_id: int) -> bool:
        """Check if session is valid."""
        if user_id not in self.sessions:
            return False
        
        session = self.sessions[user_id]
        elapsed = (datetime.now() - session['last_activity']).total_seconds()
        
        if elapsed > self.timeout_minutes * 60:
            self.end_session(user_id)
            return False
        
        return True
    
    def refresh_activity(self, user_id: int):
        """Update last activity time."""
        if user_id in self.sessions:
            self.sessions[user_id]['last_activity'] = datetime.now()
    
    def end_session(self, user_id: int):
        """End user session."""
        if user_id in self.sessions:
            del self.sessions[user_id]
    
    def get_session_info(self, user_id: int) -> dict:
        """Get session information."""
        if user_id not in self.sessions:
            return None
        
        session = self.sessions[user_id]
        elapsed = (datetime.now() - session['last_activity']).total_seconds()
        remaining = max(0, self.timeout_minutes * 60 - elapsed)
        
        return {
            'user_id': user_id,
            'created': session['created'],
            'last_activity': session['last_activity'],
            'remaining_seconds': int(remaining),
            'data': session['data']
        }


class GPACalculator:
    """GPA calculation utility."""
    
    GRADE_POINTS = {
        'A+': 4.0, 'A': 4.0, 'A-': 3.7,
        'B+': 3.3, 'B': 3.0, 'B-': 2.7,
        'C+': 2.3, 'C': 2.0, 'C-': 1.7,
        'D+': 1.3, 'D': 1.0, 'D-': 0.7,
        'F': 0.0
    }
    
    @classmethod
    def letter_to_points(cls, letter: str) -> float:
        """Convert letter grade to points."""
        return cls.GRADE_POINTS.get(letter.upper(), 0.0)
    
    @classmethod
    def calculate_gpa(cls, grades: list) -> dict:
        """
        Calculate GPA from list of grades.
        
        Args:
            grades: List of {'letter': str, 'credits': int}
        
        Returns:
            GPA calculation result
        """
        if not grades:
            return {'gpa': 0.0, 'total_credits': 0, 'total_points': 0.0}
        
        total_points = 0.0
        total_credits = 0
        
        for grade in grades:
            credits = grade.get('credits', 3)  # Default 3 credits
            points = cls.letter_to_points(grade['letter'])
            total_points += points * credits
            total_credits += credits
        
        gpa = total_points / total_credits if total_credits > 0 else 0.0
        
        return {
            'gpa': round(gpa, 2),
            'total_credits': total_credits,
            'total_points': round(total_points, 2),
            'grade_count': len(grades)
        }
    
    @classmethod
    def get_gpa_classification(cls, gpa: float) -> str:
        """Get classification based on GPA."""
        if gpa >= 3.9:
            return "Summa Cum Laude"
        elif gpa >= 3.7:
            return "Magna Cum Laude"
        elif gpa >= 3.5:
            return "Cum Laude"
        elif gpa >= 3.0:
            return "Good Standing"
        elif gpa >= 2.0:
            return "Satisfactory"
        else:
            return "Academic Probation"


class TranscriptGenerator:
    """Generate student academic transcripts."""
    
    def __init__(self):
        from src.database.connection import get_database
        self.db = get_database()
    
    def generate_transcript(self, student_id: int) -> dict:
        """Generate complete transcript for student."""
        # Get student info
        student = self.db.fetch_one(
            "SELECT * FROM STUDENT WHERE student_id = ?",
            (student_id,)
        )
        
        if not student:
            return None
        
        # Get all grades
        grades = self.db.fetch_all("""
            SELECT g.*, c.course_code, c.course_name FROM GRADES g
            JOIN COURSE c ON g.course_id = c.course_id
            WHERE g.student_id = ? AND g.is_published = 1
            ORDER BY c.course_code
        """, (student_id,))
        
        # Calculate GPA
        grade_list = [{'letter': g['grade_letter'], 'credits': 3} for g in grades]
        gpa_result = GPACalculator.calculate_gpa(grade_list)
        
        # Get attendance summary
        attendance = self.db.fetch_all("""
            SELECT status, COUNT(*) as count FROM ATTENDANCE
            WHERE student_id = ?
            GROUP BY status
        """, (student_id,))
        
        attendance_summary = {a['status']: a['count'] for a in attendance}
        
        return {
            'student': dict(student),
            'grades': [dict(g) for g in grades],
            'gpa': gpa_result,
            'classification': GPACalculator.get_gpa_classification(gpa_result['gpa']),
            'attendance': attendance_summary,
            'generated_at': datetime.now().isoformat()
        }
    
    def export_transcript_text(self, student_id: int) -> str:
        """Export transcript as text."""
        transcript = self.generate_transcript(student_id)
        if not transcript:
            return "Student not found"
        
        lines = [
            "=" * 60,
            "           ACADEMIC TRANSCRIPT",
            "    Secure Student Records Management System",
            "=" * 60,
            "",
            f"Student Name: {transcript['student']['full_name']}",
            f"Student ID: {student_id}",
            f"Department: {transcript['student'].get('department', 'N/A')}",
            f"Generated: {transcript['generated_at'][:10]}",
            "",
            "-" * 60,
            "COURSES AND GRADES",
            "-" * 60,
            ""
        ]
        
        for grade in transcript['grades']:
            lines.append(f"  {grade['course_code']}: {grade['course_name']}")
            lines.append(f"    Grade: {grade['grade_letter']}")
            lines.append("")
        
        lines.extend([
            "-" * 60,
            "ACADEMIC SUMMARY",
            "-" * 60,
            f"  GPA: {transcript['gpa']['gpa']:.2f}",
            f"  Total Credits: {transcript['gpa']['total_credits']}",
            f"  Classification: {transcript['classification']}",
            "",
            "-" * 60,
            "ATTENDANCE SUMMARY",
            "-" * 60,
        ])
        
        for status, count in transcript['attendance'].items():
            lines.append(f"  {status}: {count}")
        
        lines.extend([
            "",
            "=" * 60,
            "  This is an official document.",
            "=" * 60
        ])
        
        return "\n".join(lines)


class BulkOperations:
    """Bulk data operations for admin."""
    
    def __init__(self):
        from src.database.connection import get_database
        self.db = get_database()
    
    def bulk_publish_grades(self, course_id: int, user_id: int) -> dict:
        """Publish all unpublished grades for a course."""
        result = self.db.execute("""
            UPDATE GRADES SET is_published = 1, updated_at = ?
            WHERE course_id = ? AND is_published = 0
        """, (datetime.now(), course_id))
        self.db.commit()
        
        return {'published': result.rowcount if hasattr(result, 'rowcount') else 0}
    
    def bulk_mark_attendance(self, course_id: int, date: str, status: str,
                              recorded_by: int) -> dict:
        """Mark attendance for all enrolled students."""
        from src.database.models import EnrollmentModel
        
        enrollments = self.db.fetch_all("""
            SELECT student_id FROM ENROLLMENT 
            WHERE course_id = ? AND status = 'active'
        """, (course_id,))
        
        count = 0
        for enrollment in enrollments:
            try:
                self.db.execute("""
                    INSERT INTO ATTENDANCE (student_id, course_id, attendance_date, status, recorded_by)
                    VALUES (?, ?, ?, ?, ?)
                """, (enrollment['student_id'], course_id, date, status, recorded_by))
                count += 1
            except:
                # Already exists, update
                self.db.execute("""
                    UPDATE ATTENDANCE SET status = ?, recorded_by = ?
                    WHERE student_id = ? AND course_id = ? AND attendance_date = ?
                """, (status, recorded_by, enrollment['student_id'], course_id, date))
                count += 1
        
        self.db.commit()
        return {'updated': count}
    
    def bulk_create_notifications(self, user_ids: list, title: str, message: str,
                                   notification_type: str = 'info') -> dict:
        """Send notification to multiple users."""
        count = 0
        for user_id in user_ids:
            try:
                self.db.execute("""
                    INSERT INTO NOTIFICATIONS (user_id, title, message, notification_type)
                    VALUES (?, ?, ?, ?)
                """, (user_id, title, message, notification_type))
                count += 1
            except:
                pass
        
        self.db.commit()
        return {'sent': count}


# Global instances
_tfa_manager = None
_session_manager = None

def get_tfa_manager() -> TwoFactorAuth:
    """Get global 2FA manager."""
    global _tfa_manager
    if _tfa_manager is None:
        _tfa_manager = TwoFactorAuth()
    return _tfa_manager

def get_session_manager() -> SessionManager:
    """Get global session manager."""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager
