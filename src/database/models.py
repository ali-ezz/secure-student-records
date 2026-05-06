"""
SRMS - Database Models
Data models with integrated security features
"""

import sys
import os
from datetime import datetime
from typing import Optional, List, Dict, Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from config import SecurityLevel, ROLE_CLEARANCE
from src.security.encryption import get_encryption_manager
from src.security.rbac import get_rbac_manager
from src.security.mls import get_mls_manager
from src.security.inference_control import get_inference_controller
from src.database.connection import get_database


class SecureModel:
    """
    Base class for secure data models.
    Integrates all security controls into data operations.
    """
    
    table_name = None
    classification = SecurityLevel.PUBLIC
    encrypted_fields = []
    
    def __init__(self):
        self.db = get_database()
        self.encryption = get_encryption_manager()
        self.rbac = get_rbac_manager()
        self.mls = get_mls_manager()
        self.inference = get_inference_controller()
    
    def _encrypt_record(self, record: dict) -> dict:
        """Encrypt sensitive fields in record."""
        encrypted = record.copy()
        for field in self.encrypted_fields:
            if field in encrypted and encrypted[field] is not None:
                encrypted[f"{field}_encrypted"] = self.encryption.encrypt(str(encrypted[field]))
        return encrypted
    
    def _decrypt_record(self, record: dict) -> dict:
        """Decrypt sensitive fields in record."""
        decrypted = record.copy()
        for field in self.encrypted_fields:
            enc_field = f"{field}_encrypted"
            if enc_field in decrypted and decrypted[enc_field]:
                try:
                    decrypted[field] = self.encryption.decrypt(decrypted[enc_field])
                except Exception:
                    decrypted[field] = "[ENCRYPTED]"
        return decrypted
    
    def check_access(self, role: str, operation: str, user_id: int = None, 
                     target_id: int = None) -> bool:
        """Check if operation is allowed for role."""
        # RBAC check
        if not self.rbac.has_permission(role, self.table_name, operation, user_id, target_id):
            return False
        
        # MLS check
        mls_result = self.mls.check_access(role, self.table_name, operation)
        if not mls_result['allowed']:
            return False
        
        return True
    
    def audit_log(self, user_id: int, action: str, record_id: int = None,
                  old_value: str = None, new_value: str = None):
        """Log action to audit trail."""
        self.db.execute("""
            INSERT INTO AUDIT_LOG (user_id, action, table_name, record_id, 
                                   old_value, new_value, security_level, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, action, self.table_name, record_id, old_value, new_value,
              self.classification, datetime.now()))
        self.db.commit()


class UserModel(SecureModel):
    """User model with authentication and role management."""
    
    table_name = 'USERS'
    classification = SecurityLevel.TOP_SECRET
    encrypted_fields = ['username']
    
    def create_user(self, username: str, password: str, role: str,
                    linked_id: int = None, current_user_role: str = 'Admin') -> dict:
        """
        Create a new user.
        
        Args:
            username: Unique username
            password: Plain text password (will be hashed)
            role: User role (Admin, Instructor, TA, Student, Guest)
            linked_id: Optional linked Student/Instructor ID
            current_user_role: Role of user creating this account
        
        Returns:
            Created user dict or None
        """
        # Only Admin can create users
        if not self.rbac.has_permission(current_user_role, self.table_name, 'INSERT'):
            return {'error': 'Permission denied: Only Admin can create users'}
        
        # Hash password
        password_hash, salt = self.encryption.hash_password(password)
        clearance = ROLE_CLEARANCE.get(role, 0)
        
        try:
            self.db.execute("""
                INSERT INTO USERS (username, password_hash, salt, role, clearance_level, linked_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (username, password_hash, salt, role, clearance, linked_id))
            self.db.commit()
            
            return self.get_user_by_username(username)
        except Exception as e:
            return {'error': str(e)}
    
    def authenticate(self, username: str, password: str) -> Optional[dict]:
        """
        Authenticate user.
        
        Args:
            username: Username
            password: Plain text password
        
        Returns:
            User dict if authenticated, None otherwise
        """
        user = self.db.fetch_one("""
            SELECT * FROM USERS WHERE username = ? AND is_active = 1
        """, (username,))
        
        if user and self.encryption.verify_password(password, user['password_hash']):
            # Reset failed attempts and update last login
            self.db.execute("""
                UPDATE USERS SET failed_login_attempts = 0, last_login = ?
                WHERE user_id = ?
            """, (datetime.now(), user['user_id']))
            self.db.commit()
            
            self.audit_log(user['user_id'], 'LOGIN')
            return dict(user)
        
        # Track failed attempts
        if user:
            self.db.execute("""
                UPDATE USERS SET failed_login_attempts = failed_login_attempts + 1
                WHERE user_id = ?
            """, (user['user_id'],))
            self.db.commit()
            self.audit_log(user['user_id'], 'LOGIN_FAILED')
        
        return None
    
    def get_user_by_username(self, username: str) -> Optional[dict]:
        """Get user by username."""
        return self.db.fetch_one("SELECT * FROM USERS WHERE username = ?", (username,))
    
    def get_user_by_id(self, user_id: int) -> Optional[dict]:
        """Get user by ID."""
        return self.db.fetch_one("SELECT * FROM USERS WHERE user_id = ?", (user_id,))
    
    def get_all_users(self, current_role: str = 'Admin') -> list:
        """Get all users (Admin only)."""
        if not self.rbac.has_permission(current_role, self.table_name, 'SELECT'):
            return []
        return self.db.fetch_all("SELECT user_id, username, role, clearance_level, is_active, last_login FROM USERS")
    
    def update_role(self, user_id: int, new_role: str, admin_id: int) -> bool:
        """Update user role (Admin only)."""
        old_user = self.get_user_by_id(user_id)
        if not old_user:
            return False
        
        new_clearance = ROLE_CLEARANCE.get(new_role, 0)
        self.db.execute("""
            UPDATE USERS SET role = ?, clearance_level = ?, updated_at = ?
            WHERE user_id = ?
        """, (new_role, new_clearance, datetime.now(), user_id))
        self.db.commit()
        
        self.audit_log(admin_id, 'ROLE_CHANGE', user_id, 
                       old_user['role'], new_role)
        return True
    
    def delete_user(self, user_id: int, admin_id: int) -> bool:
        """Soft delete user (Admin only)."""
        self.db.execute("""
            UPDATE USERS SET is_active = 0, updated_at = ? WHERE user_id = ?
        """, (datetime.now(), user_id))
        self.db.commit()
        
        self.audit_log(admin_id, 'USER_DELETED', user_id)
        return True


class StudentModel(SecureModel):
    """Student data model with encryption."""
    
    table_name = 'STUDENT'
    classification = SecurityLevel.CONFIDENTIAL
    encrypted_fields = ['student_id', 'phone']
    
    def create_student(self, full_name: str, email: str, phone: str = None,
                       dob: str = None, department: str = None,
                       current_role: str = 'Admin') -> dict:
        """Create a new student record."""
        if not self.check_access(current_role, 'INSERT'):
            return {'error': 'Permission denied'}
        
        # Encrypt sensitive fields
        phone_encrypted = self.encryption.encrypt(phone) if phone else None
        
        try:
            cursor = self.db.execute("""
                INSERT INTO STUDENT (full_name, email, phone_encrypted, date_of_birth, department)
                VALUES (?, ?, ?, ?, ?)
            """, (full_name, email, phone_encrypted, dob, department))
            self.db.commit()
            
            # Update encrypted student_id
            student_id = cursor.lastrowid
            student_id_encrypted = self.encryption.encrypt(str(student_id))
            self.db.execute("""
                UPDATE STUDENT SET student_id_encrypted = ? WHERE student_id = ?
            """, (student_id_encrypted, student_id))
            self.db.commit()
            
            return self.get_student(student_id, current_role)
        except Exception as e:
            return {'error': str(e)}
    
    def get_student(self, student_id: int, current_role: str = 'Admin',
                    current_user_id: int = None) -> Optional[dict]:
        """Get student by ID with access control."""
        # Check if user can only access own data
        if self.rbac.can_access_own_data_only(current_role, self.table_name, 'SELECT'):
            if current_user_id != student_id:
                return None
        
        if not self.check_access(current_role, 'SELECT', current_user_id, student_id):
            return None
        
        student = self.db.fetch_one("SELECT * FROM STUDENT WHERE student_id = ?", (student_id,))
        return self._decrypt_record(student) if student else None
    
    def get_all_students(self, current_role: str = 'Admin', 
                         course_id: int = None) -> list:
        """
        Get all students with role-based filtering.
        Instructors/TAs see only assigned course students.
        """
        if not self.check_access(current_role, 'SELECT'):
            return []
        
        if current_role in ['Instructor', 'TA'] and course_id:
            # Get students enrolled in assigned course
            students = self.db.fetch_all("""
                SELECT DISTINCT s.* FROM STUDENT s
                JOIN GRADES g ON s.student_id = g.student_id
                WHERE g.course_id = ?
            """, (course_id,))
        else:
            students = self.db.fetch_all("SELECT * FROM STUDENT")
        
        return [self._decrypt_record(s) for s in students]
    
    def update_student(self, student_id: int, updates: dict,
                       current_role: str = 'Admin', user_id: int = None) -> bool:
        """Update student record."""
        if not self.check_access(current_role, 'UPDATE', user_id, student_id):
            return False
        
        # Encrypt phone if being updated
        if 'phone' in updates:
            updates['phone_encrypted'] = self.encryption.encrypt(updates['phone'])
            del updates['phone']
        
        set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [datetime.now(), student_id]
        
        self.db.execute(f"""
            UPDATE STUDENT SET {set_clause}, updated_at = ? WHERE student_id = ?
        """, tuple(values))
        self.db.commit()
        return True


class InstructorModel(SecureModel):
    """Instructor data model."""
    
    table_name = 'INSTRUCTOR'
    classification = SecurityLevel.CONFIDENTIAL
    
    def create_instructor(self, full_name: str, email: str,
                          department: str = None, current_role: str = 'Admin') -> dict:
        """Create a new instructor record."""
        if not self.check_access(current_role, 'INSERT'):
            return {'error': 'Permission denied'}
        
        try:
            cursor = self.db.execute("""
                INSERT INTO INSTRUCTOR (full_name, email, department)
                VALUES (?, ?, ?)
            """, (full_name, email, department))
            self.db.commit()
            return {'instructor_id': cursor.lastrowid}
        except Exception as e:
            return {'error': str(e)}
    
    def get_instructor(self, instructor_id: int, current_role: str = 'Admin') -> Optional[dict]:
        """Get instructor by ID."""
        if not self.check_access(current_role, 'SELECT'):
            return None
        return self.db.fetch_one("SELECT * FROM INSTRUCTOR WHERE instructor_id = ?", (instructor_id,))
    
    def get_all_instructors(self, current_role: str = 'Admin') -> list:
        """Get all instructors."""
        if not self.check_access(current_role, 'SELECT'):
            return []
        return self.db.fetch_all("SELECT * FROM INSTRUCTOR")


class CourseModel(SecureModel):
    """Course data model."""
    
    table_name = 'COURSE'
    classification = SecurityLevel.UNCLASSIFIED
    
    def create_course(self, course_code: str, course_name: str,
                      description: str = None, public_info: str = None,
                      instructor_id: int = None, current_role: str = 'Admin') -> dict:
        """Create a new course."""
        if not self.check_access(current_role, 'INSERT'):
            return {'error': 'Permission denied'}
        
        try:
            cursor = self.db.execute("""
                INSERT INTO COURSE (course_code, course_name, description, public_info, instructor_id)
                VALUES (?, ?, ?, ?, ?)
            """, (course_code, course_name, description, public_info, instructor_id))
            self.db.commit()
            return {'course_id': cursor.lastrowid}
        except Exception as e:
            return {'error': str(e)}
    
    def get_course(self, course_id: int, current_role: str = 'Admin') -> Optional[dict]:
        """Get course by ID."""
        return self.db.fetch_one("SELECT * FROM COURSE WHERE course_id = ?", (course_id,))
    
    def get_all_courses(self, current_role: str = 'Admin') -> list:
        """Get all courses (or just public info for Guest)."""
        if current_role == 'Guest':
            return self.db.fetch_all("""
                SELECT course_id, course_code, course_name, public_info FROM COURSE
            """)
        return self.db.fetch_all("SELECT * FROM COURSE")
    
    def get_public_courses(self) -> list:
        """Get public course information (Guest accessible)."""
        return self.db.fetch_all("""
            SELECT course_id, course_code, course_name, public_info FROM COURSE
        """)


class GradesModel(SecureModel):
    """Grades data model with encryption."""
    
    table_name = 'GRADES'
    classification = SecurityLevel.SECRET
    encrypted_fields = ['grade_value', 'student_id']
    
    def create_grade(self, student_id: int, course_id: int, grade_value: float,
                     grade_letter: str, entered_by: int, is_published: bool = False,
                     current_role: str = 'Instructor') -> dict:
        """Create a new grade entry."""
        if not self.check_access(current_role, 'INSERT'):
            return {'error': 'Permission denied: Only Admin/Instructor can add grades'}
        
        # Encrypt grade value
        grade_encrypted = self.encryption.encrypt(str(grade_value))
        student_id_encrypted = self.encryption.encrypt(str(student_id))
        
        try:
            cursor = self.db.execute("""
                INSERT INTO GRADES (student_id, student_id_encrypted, course_id, 
                                    grade_value_encrypted, grade_letter, is_published, entered_by)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (student_id, student_id_encrypted, course_id, grade_encrypted, 
                  grade_letter, 1 if is_published else 0, entered_by))
            self.db.commit()
            return {'grade_id': cursor.lastrowid}
        except Exception as e:
            return {'error': str(e)}
    
    def get_student_grades(self, student_id: int, current_role: str = 'Admin',
                           current_user_id: int = None) -> list:
        """Get grades for a student."""
        # Students can only see their own published grades
        if current_role == 'Student':
            if current_user_id != student_id:
                return []
            grades = self.db.fetch_all("""
                SELECT g.*, c.course_name FROM GRADES g
                JOIN COURSE c ON g.course_id = c.course_id
                WHERE g.student_id = ? AND g.is_published = 1
            """, (student_id,))
        elif current_role == 'TA':
            return []  # TAs cannot view grades
        else:
            if not self.check_access(current_role, 'SELECT'):
                return []
            grades = self.db.fetch_all("""
                SELECT g.*, c.course_name FROM GRADES g
                JOIN COURSE c ON g.course_id = c.course_id
                WHERE g.student_id = ?
            """, (student_id,))
        
        # Decrypt and return
        return [self._decrypt_record(g) for g in grades]
    
    def get_course_grades(self, course_id: int, current_role: str = 'Admin',
                          user_id: int = None) -> list:
        """Get all grades for a course."""
        if current_role == 'TA':
            return []  # TAs cannot view grades
        
        if not self.check_access(current_role, 'SELECT'):
            return []
        
        # Apply inference control
        count = self.db.fetch_one(
            "SELECT COUNT(*) as count FROM GRADES WHERE course_id = ?", (course_id,)
        )['count']
        
        if not self.inference.check_query_set_size(count)['allowed']:
            return [{'error': 'Query blocked: Insufficient records for privacy protection'}]
        
        grades = self.db.fetch_all("""
            SELECT g.*, s.full_name as student_name FROM GRADES g
            JOIN STUDENT s ON g.student_id = s.student_id
            WHERE g.course_id = ?
        """, (course_id,))
        
        return [self._decrypt_record(g) for g in grades]
    
    def update_grade(self, grade_id: int, grade_value: float, grade_letter: str,
                     current_role: str = 'Instructor', user_id: int = None) -> bool:
        """Update a grade."""
        if not self.check_access(current_role, 'UPDATE'):
            return False
        
        grade_encrypted = self.encryption.encrypt(str(grade_value))
        self.db.execute("""
            UPDATE GRADES SET grade_value_encrypted = ?, grade_letter = ?, updated_at = ?
            WHERE grade_id = ?
        """, (grade_encrypted, grade_letter, datetime.now(), grade_id))
        self.db.commit()
        
        self.audit_log(user_id, 'GRADE_UPDATE', grade_id)
        return True
    
    def publish_grades(self, course_id: int, current_role: str = 'Instructor',
                       user_id: int = None) -> bool:
        """Publish all grades for a course."""
        if not self.check_access(current_role, 'UPDATE'):
            return False
        
        self.db.execute("""
            UPDATE GRADES SET is_published = 1, updated_at = ?
            WHERE course_id = ?
        """, (datetime.now(), course_id))
        self.db.commit()
        
        self.audit_log(user_id, 'GRADES_PUBLISHED', course_id)
        return True


class AttendanceModel(SecureModel):
    """Attendance data model."""
    
    table_name = 'ATTENDANCE'
    classification = SecurityLevel.SECRET
    
    def record_attendance(self, student_id: int, course_id: int, status: str,
                          attendance_date: str, recorded_by: int,
                          current_role: str = 'TA') -> dict:
        """Record student attendance."""
        if not self.check_access(current_role, 'INSERT'):
            return {'error': 'Permission denied'}
        
        try:
            cursor = self.db.execute("""
                INSERT INTO ATTENDANCE (student_id, course_id, status, attendance_date, recorded_by)
                VALUES (?, ?, ?, ?, ?)
            """, (student_id, course_id, status, attendance_date, recorded_by))
            self.db.commit()
            return {'attendance_id': cursor.lastrowid}
        except Exception as e:
            # Update if exists
            self.db.execute("""
                UPDATE ATTENDANCE SET status = ?, recorded_by = ?, updated_at = ?
                WHERE student_id = ? AND course_id = ? AND attendance_date = ?
            """, (status, recorded_by, datetime.now(), student_id, course_id, attendance_date))
            self.db.commit()
            return {'updated': True}
    
    def get_student_attendance(self, student_id: int, current_role: str = 'Admin',
                                current_user_id: int = None, course_id: int = None) -> list:
        """Get attendance for a student."""
        # Students can only see their own attendance
        if current_role == 'Student' and current_user_id != student_id:
            return []
        
        if not self.check_access(current_role, 'SELECT', current_user_id, student_id):
            return []
        
        if course_id:
            return self.db.fetch_all("""
                SELECT a.*, c.course_name FROM ATTENDANCE a
                JOIN COURSE c ON a.course_id = c.course_id
                WHERE a.student_id = ? AND a.course_id = ?
                ORDER BY a.attendance_date DESC
            """, (student_id, course_id))
        
        return self.db.fetch_all("""
            SELECT a.*, c.course_name FROM ATTENDANCE a
            JOIN COURSE c ON a.course_id = c.course_id
            WHERE a.student_id = ?
            ORDER BY a.attendance_date DESC
        """, (student_id,))
    
    def get_course_attendance(self, course_id: int, attendance_date: str,
                               current_role: str = 'Admin') -> list:
        """Get attendance for a course on a date."""
        if not self.check_access(current_role, 'SELECT'):
            return []
        
        # Apply inference control
        count = self.db.fetch_one(
            "SELECT COUNT(*) as count FROM ATTENDANCE WHERE course_id = ? AND attendance_date = ?",
            (course_id, attendance_date)
        )['count']
        
        if not self.inference.check_query_set_size(count)['allowed']:
            return [{'error': 'Query blocked: Insufficient records for privacy protection'}]
        
        return self.db.fetch_all("""
            SELECT a.*, s.full_name as student_name FROM ATTENDANCE a
            JOIN STUDENT s ON a.student_id = s.student_id
            WHERE a.course_id = ? AND a.attendance_date = ?
        """, (course_id, attendance_date))


class RoleRequestModel(SecureModel):
    """Role request model for Part B: Role upgrade workflow."""
    
    table_name = 'ROLE_REQUESTS'
    classification = SecurityLevel.CONFIDENTIAL
    
    def submit_request(self, user_id: int, username: str, current_role: str,
                       requested_role: str, reason: str, comments: str = None) -> dict:
        """Submit a role upgrade request."""
        # Validate role upgrade path
        valid_upgrades = {
            'Student': ['TA'],
            'TA': ['Instructor']
        }
        
        if current_role not in valid_upgrades:
            return {'error': 'Your role cannot be upgraded through this system'}
        
        if requested_role not in valid_upgrades.get(current_role, []):
            return {'error': f'Cannot upgrade from {current_role} to {requested_role}'}
        
        # Check for pending request
        existing = self.db.fetch_one("""
            SELECT * FROM ROLE_REQUESTS 
            WHERE user_id = ? AND status = 'Pending'
        """, (user_id,))
        
        if existing:
            return {'error': 'You already have a pending role request'}
        
        try:
            cursor = self.db.execute("""
                INSERT INTO ROLE_REQUESTS (user_id, username, current_role, requested_role, reason, comments)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, username, current_role, requested_role, reason, comments))
            self.db.commit()
            return {'request_id': cursor.lastrowid, 'status': 'Pending'}
        except Exception as e:
            return {'error': str(e)}
    
    def get_pending_requests(self, current_role: str = 'Admin') -> list:
        """Get all pending role requests (Admin only)."""
        if current_role != 'Admin':
            return []
        
        return self.db.fetch_all("""
            SELECT * FROM ROLE_REQUESTS 
            WHERE status = 'Pending'
            ORDER BY date_submitted ASC
        """)
    
    def get_user_requests(self, user_id: int) -> list:
        """Get all requests for a user."""
        return self.db.fetch_all("""
            SELECT * FROM ROLE_REQUESTS 
            WHERE user_id = ?
            ORDER BY date_submitted DESC
        """, (user_id,))
    
    def approve_request(self, request_id: int, admin_username: str,
                        admin_comments: str = None) -> dict:
        """Approve a role request."""
        request = self.db.fetch_one(
            "SELECT * FROM ROLE_REQUESTS WHERE request_id = ? AND status = 'Pending'",
            (request_id,)
        )
        
        if not request:
            return {'error': 'Request not found or already processed'}
        
        # Update request status
        self.db.execute("""
            UPDATE ROLE_REQUESTS 
            SET status = 'Approved', date_processed = ?, processed_by = ?, admin_comments = ?
            WHERE request_id = ?
        """, (datetime.now(), admin_username, admin_comments, request_id))
        
        # Update user's role
        user_model = UserModel()
        new_clearance = ROLE_CLEARANCE.get(request['requested_role'], 0)
        
        self.db.execute("""
            UPDATE USERS SET role = ?, clearance_level = ?, updated_at = ?
            WHERE user_id = ?
        """, (request['requested_role'], new_clearance, datetime.now(), request['user_id']))
        
        self.db.commit()
        
        return {
            'success': True,
            'message': f"Role upgraded from {request['current_role']} to {request['requested_role']}"
        }
    
    def deny_request(self, request_id: int, admin_username: str,
                     admin_comments: str = None) -> dict:
        """Deny a role request."""
        request = self.db.fetch_one(
            "SELECT * FROM ROLE_REQUESTS WHERE request_id = ? AND status = 'Pending'",
            (request_id,)
        )
        
        if not request:
            return {'error': 'Request not found or already processed'}
        
        self.db.execute("""
            UPDATE ROLE_REQUESTS 
            SET status = 'Denied', date_processed = ?, processed_by = ?, admin_comments = ?
            WHERE request_id = ?
        """, (datetime.now(), admin_username, admin_comments, request_id))
        self.db.commit()
        
        return {'success': True, 'message': 'Request denied'}


class NotificationModel(SecureModel):
    """Notification model for alerts and messages."""
    
    table_name = 'NOTIFICATIONS'
    classification = SecurityLevel.UNCLASSIFIED
    
    def create_notification(self, user_id: int, title: str, message: str,
                            notification_type: str = 'info') -> dict:
        """Create a new notification."""
        try:
            cursor = self.db.execute("""
                INSERT INTO NOTIFICATIONS (user_id, title, message, notification_type)
                VALUES (?, ?, ?, ?)
            """, (user_id, title, message, notification_type))
            self.db.commit()
            return {'notification_id': cursor.lastrowid}
        except Exception as e:
            return {'error': str(e)}
    
    def get_user_notifications(self, user_id: int, unread_only: bool = False) -> list:
        """Get notifications for a user."""
        if unread_only:
            return self.db.fetch_all("""
                SELECT * FROM NOTIFICATIONS WHERE user_id = ? AND is_read = 0
                ORDER BY created_at DESC
            """, (user_id,))
        return self.db.fetch_all("""
            SELECT * FROM NOTIFICATIONS WHERE user_id = ?
            ORDER BY created_at DESC LIMIT 50
        """, (user_id,))
    
    def get_unread_count(self, user_id: int) -> int:
        """Get count of unread notifications."""
        result = self.db.fetch_one("""
            SELECT COUNT(*) as count FROM NOTIFICATIONS 
            WHERE user_id = ? AND is_read = 0
        """, (user_id,))
        return result['count'] if result else 0
    
    def mark_read(self, notification_id: int, user_id: int) -> bool:
        """Mark notification as read."""
        self.db.execute("""
            UPDATE NOTIFICATIONS SET is_read = 1 
            WHERE notification_id = ? AND user_id = ?
        """, (notification_id, user_id))
        self.db.commit()
        return True
    
    def mark_all_read(self, user_id: int) -> bool:
        """Mark all notifications as read."""
        self.db.execute("""
            UPDATE NOTIFICATIONS SET is_read = 1 WHERE user_id = ?
        """, (user_id,))
        self.db.commit()
        return True


class AnnouncementModel(SecureModel):
    """Announcement model for course and system announcements."""
    
    table_name = 'ANNOUNCEMENTS'
    classification = SecurityLevel.UNCLASSIFIED
    
    def create_announcement(self, title: str, content: str, author_id: int,
                           course_id: int = None, visibility: str = 'all',
                           is_pinned: bool = False, current_role: str = 'Admin') -> dict:
        """Create a new announcement."""
        if current_role not in ['Admin', 'Instructor']:
            return {'error': 'Only Admin and Instructors can create announcements'}
        
        try:
            cursor = self.db.execute("""
                INSERT INTO ANNOUNCEMENTS (course_id, title, content, author_id, is_pinned, visibility)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (course_id, title, content, author_id, 1 if is_pinned else 0, visibility))
            self.db.commit()
            return {'announcement_id': cursor.lastrowid}
        except Exception as e:
            return {'error': str(e)}
    
    def get_announcements(self, current_role: str = 'Student', course_id: int = None) -> list:
        """Get visible announcements."""
        role_visibility = {
            'Admin': ['all', 'students', 'staff', 'admin'],
            'Instructor': ['all', 'students', 'staff'],
            'TA': ['all', 'students', 'staff'],
            'Student': ['all', 'students'],
            'Guest': ['all']
        }
        
        visible = role_visibility.get(current_role, ['all'])
        placeholders = ','.join(['?' for _ in visible])
        
        if course_id:
            return self.db.fetch_all(f"""
                SELECT a.*, u.username as author_name FROM ANNOUNCEMENTS a
                LEFT JOIN USERS u ON a.author_id = u.user_id
                WHERE (a.course_id = ? OR a.course_id IS NULL)
                AND a.visibility IN ({placeholders})
                ORDER BY a.is_pinned DESC, a.created_at DESC
            """, (course_id, *visible))
        
        return self.db.fetch_all(f"""
            SELECT a.*, u.username as author_name FROM ANNOUNCEMENTS a
            LEFT JOIN USERS u ON a.author_id = u.user_id
            WHERE a.visibility IN ({placeholders})
            ORDER BY a.is_pinned DESC, a.created_at DESC
        """, tuple(visible))
    
    def delete_announcement(self, announcement_id: int, current_role: str = 'Admin') -> bool:
        """Delete an announcement."""
        if current_role != 'Admin':
            return False
        self.db.execute("DELETE FROM ANNOUNCEMENTS WHERE announcement_id = ?", (announcement_id,))
        self.db.commit()
        return True


class EnrollmentModel(SecureModel):
    """Enrollment model for student course registration."""
    
    table_name = 'ENROLLMENT'
    classification = SecurityLevel.CONFIDENTIAL
    
    def enroll_student(self, student_id: int, course_id: int,
                       current_role: str = 'Admin') -> dict:
        """Enroll a student in a course."""
        if current_role not in ['Admin', 'Instructor']:
            return {'error': 'Permission denied'}
        
        try:
            cursor = self.db.execute("""
                INSERT INTO ENROLLMENT (student_id, course_id)
                VALUES (?, ?)
            """, (student_id, course_id))
            self.db.commit()
            return {'enrollment_id': cursor.lastrowid}
        except Exception as e:
            return {'error': str(e)}
    
    def get_student_enrollments(self, student_id: int) -> list:
        """Get all enrollments for a student."""
        return self.db.fetch_all("""
            SELECT e.*, c.course_code, c.course_name FROM ENROLLMENT e
            JOIN COURSE c ON e.course_id = c.course_id
            WHERE e.student_id = ? AND e.status = 'active'
        """, (student_id,))
    
    def get_course_enrollments(self, course_id: int, current_role: str = 'Admin') -> list:
        """Get all students enrolled in a course."""
        if current_role == 'Guest':
            return []
        return self.db.fetch_all("""
            SELECT e.*, s.full_name, s.email FROM ENROLLMENT e
            JOIN STUDENT s ON e.student_id = s.student_id
            WHERE e.course_id = ? AND e.status = 'active'
        """, (course_id,))
    
    def drop_course(self, student_id: int, course_id: int,
                    current_role: str = 'Student', current_user_id: int = None) -> bool:
        """Drop a course."""
        if current_role == 'Student' and current_user_id != student_id:
            return False
        
        self.db.execute("""
            UPDATE ENROLLMENT SET status = 'dropped' 
            WHERE student_id = ? AND course_id = ?
        """, (student_id, course_id))
        self.db.commit()
        return True


class SystemSettingsModel(SecureModel):
    """System settings model."""
    
    table_name = 'SYSTEM_SETTINGS'
    classification = SecurityLevel.TOP_SECRET
    
    def get_setting(self, key: str) -> Optional[str]:
        """Get a system setting."""
        result = self.db.fetch_one(
            "SELECT setting_value, setting_type FROM SYSTEM_SETTINGS WHERE setting_key = ?",
            (key,)
        )
        if result:
            if result['setting_type'] == 'boolean':
                return result['setting_value'] == 'true'
            elif result['setting_type'] == 'integer':
                return int(result['setting_value'])
            return result['setting_value']
        return None
    
    def set_setting(self, key: str, value: str, admin_id: int = None,
                    current_role: str = 'Admin') -> bool:
        """Set a system setting (Admin only)."""
        if current_role != 'Admin':
            return False
        
        self.db.execute("""
            UPDATE SYSTEM_SETTINGS SET setting_value = ?, updated_at = ?, updated_by = ?
            WHERE setting_key = ?
        """, (str(value), datetime.now(), admin_id, key))
        self.db.commit()
        return True
    
    def get_all_settings(self, current_role: str = 'Admin') -> list:
        """Get all settings (Admin only)."""
        if current_role != 'Admin':
            return []
        return self.db.fetch_all("SELECT * FROM SYSTEM_SETTINGS")

