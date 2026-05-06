"""
SRMS - Database Seed Data
Initial data for testing all security features
"""

import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.database.connection import get_database
from src.security.encryption import get_encryption_manager


def seed_database():
    """Seed database with test data for all roles."""
    db = get_database()
    encryption = get_encryption_manager()
    
    print("🌱 Seeding SRMS Database...")
    
    # Clear existing data (for fresh start)
    tables = ['AUDIT_LOG', 'ROLE_REQUESTS', 'ATTENDANCE', 'GRADES', 
              'COURSE_ASSIGNMENTS', 'COURSE', 'INSTRUCTOR', 'STUDENT', 'USERS',
              'NOTIFICATIONS', 'ANNOUNCEMENTS', 'ENROLLMENT', 'SESSIONS']
    for table in tables:
        try:
            db.execute(f"DELETE FROM {table}")
        except Exception:
            pass
    db.commit()
    
    # =====================================
    # Create Users with different roles
    # =====================================
    print("  👤 Creating users...")
    
    users = [
        ('admin', 'admin123', 'Admin', 4),
        ('prof_smith', 'prof123', 'Instructor', 3),
        ('prof_jones', 'prof123', 'Instructor', 3),
        ('ta_williams', 'ta123', 'TA', 2),
        ('ta_brown', 'ta123', 'TA', 2),
        ('student1', 'student123', 'Student', 1),
        ('student2', 'student123', 'Student', 1),
        ('student3', 'student123', 'Student', 1),
        ('student4', 'student123', 'Student', 1),
        ('student5', 'student123', 'Student', 1),
        ('guest', 'guest123', 'Guest', 0),
    ]
    
    for username, password, role, clearance in users:
        password_hash, salt = encryption.hash_password(password)
        db.execute("""
            INSERT INTO USERS (username, password_hash, salt, role, clearance_level)
            VALUES (?, ?, ?, ?, ?)
        """, (username, password_hash, salt, role, clearance))
    
    db.commit()
    print(f"    ✓ Created {len(users)} users")
    
    # =====================================
    # Create Instructors
    # =====================================
    print("  👨‍🏫 Creating instructors...")
    
    instructors = [
        ('Dr. John Smith', 'john.smith@university.edu', 'Computer Science'),
        ('Dr. Sarah Jones', 'sarah.jones@university.edu', 'Information Security'),
    ]
    
    for name, email, dept in instructors:
        db.execute("""
            INSERT INTO INSTRUCTOR (full_name, email, department)
            VALUES (?, ?, ?)
        """, (name, email, dept))
    
    # Link instructors to users
    db.execute("UPDATE USERS SET linked_id = 1 WHERE username = 'prof_smith'")
    db.execute("UPDATE USERS SET linked_id = 2 WHERE username = 'prof_jones'")
    
    db.commit()
    print(f"    ✓ Created {len(instructors)} instructors")
    
    # =====================================
    # Create Students with encrypted data
    # =====================================
    print("  🎓 Creating students...")
    
    students = [
        ('Alice Johnson', 'alice.j@student.edu', '555-0101', '2002-03-15', 'Computer Science'),
        ('Bob Williams', 'bob.w@student.edu', '555-0102', '2001-07-22', 'Information Security'),
        ('Carol Davis', 'carol.d@student.edu', '555-0103', '2002-11-08', 'Computer Science'),
        ('David Miller', 'david.m@student.edu', '555-0104', '2001-05-30', 'Data Science'),
        ('Emma Wilson', 'emma.w@student.edu', '555-0105', '2002-09-12', 'Information Security'),
    ]
    
    for i, (name, email, phone, dob, dept) in enumerate(students, 1):
        phone_encrypted = encryption.encrypt(phone)
        student_id_encrypted = encryption.encrypt(str(i))
        db.execute("""
            INSERT INTO STUDENT (full_name, email, phone_encrypted, date_of_birth, department, student_id_encrypted)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, email, phone_encrypted, dob, dept, student_id_encrypted))
    
    # Link students to users
    for i in range(1, 6):
        db.execute(f"UPDATE USERS SET linked_id = {i} WHERE username = 'student{i}'")
    
    db.commit()
    print(f"    ✓ Created {len(students)} students")
    
    # =====================================
    # Create Courses
    # =====================================
    print("  📚 Creating courses...")
    
    courses = [
        ('CS101', 'Introduction to Programming', 
         'Fundamentals of programming using Python', 
         'Open to all students. No prerequisites.', 1),
        ('CS201', 'Database Security', 
         'Advanced concepts in database security and access control', 
         'Prerequisites: CS101. Focus on security models.', 1),
        ('IS301', 'Information Security', 
         'Comprehensive study of information security principles', 
         'Advanced course on cybersecurity.', 2),
    ]
    
    for code, name, desc, public_info, instructor_id in courses:
        db.execute("""
            INSERT INTO COURSE (course_code, course_name, description, public_info, instructor_id)
            VALUES (?, ?, ?, ?, ?)
        """, (code, name, desc, public_info, instructor_id))
    
    db.commit()
    print(f"    ✓ Created {len(courses)} courses")
    
    # =====================================
    # Create Course Assignments (TA/Instructor to Course)
    # =====================================
    print("  📋 Creating course assignments...")
    
    # Get user IDs
    prof1 = db.fetch_one("SELECT user_id FROM USERS WHERE username = 'prof_smith'")['user_id']
    prof2 = db.fetch_one("SELECT user_id FROM USERS WHERE username = 'prof_jones'")['user_id']
    ta1 = db.fetch_one("SELECT user_id FROM USERS WHERE username = 'ta_williams'")['user_id']
    ta2 = db.fetch_one("SELECT user_id FROM USERS WHERE username = 'ta_brown'")['user_id']
    
    assignments = [
        (prof1, 1, 'Instructor'),  # Prof Smith -> CS101
        (prof1, 2, 'Instructor'),  # Prof Smith -> CS201
        (prof2, 3, 'Instructor'),  # Prof Jones -> IS301
        (ta1, 1, 'TA'),            # TA Williams -> CS101
        (ta1, 2, 'TA'),            # TA Williams -> CS201
        (ta2, 3, 'TA'),            # TA Brown -> IS301
    ]
    
    for user_id, course_id, role in assignments:
        db.execute("""
            INSERT INTO COURSE_ASSIGNMENTS (user_id, course_id, role)
            VALUES (?, ?, ?)
        """, (user_id, course_id, role))
    
    db.commit()
    print(f"    ✓ Created {len(assignments)} course assignments")
    
    # =====================================
    # Create Grades (Encrypted)
    # =====================================
    print("  📊 Creating grades...")
    
    grades = [
        # CS101 grades
        (1, 1, '92.5', 'A', True),
        (2, 1, '85.0', 'B', True),
        (3, 1, '78.5', 'C+', True),
        (4, 1, '95.0', 'A', True),
        (5, 1, '88.0', 'B+', True),
        # CS201 grades (some unpublished)
        (1, 2, '88.0', 'B+', True),
        (2, 2, '91.5', 'A-', True),
        (3, 2, '82.0', 'B-', False),  # Unpublished
        (4, 2, '94.0', 'A', False),   # Unpublished
        # IS301 grades
        (2, 3, '90.0', 'A-', True),
        (3, 3, '87.5', 'B+', True),
        (5, 3, '93.0', 'A', True),
    ]
    
    instructor_user = db.fetch_one("SELECT user_id FROM USERS WHERE username = 'prof_smith'")['user_id']
    
    for student_id, course_id, grade_val, letter, published in grades:
        grade_encrypted = encryption.encrypt(grade_val)
        student_id_encrypted = encryption.encrypt(str(student_id))
        db.execute("""
            INSERT INTO GRADES (student_id, student_id_encrypted, course_id, 
                                grade_value_encrypted, grade_letter, is_published, entered_by)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (student_id, student_id_encrypted, course_id, grade_encrypted, 
              letter, 1 if published else 0, instructor_user))
    
    db.commit()
    print(f"    ✓ Created {len(grades)} grade entries")
    
    # =====================================
    # Create Attendance Records
    # =====================================
    print("  📅 Creating attendance records...")
    
    # Generate attendance for past 5 days
    today = datetime.now().date()
    statuses = ['Present', 'Present', 'Present', 'Absent', 'Late', 'Present', 'Excused']
    
    ta_user = db.fetch_one("SELECT user_id FROM USERS WHERE username = 'ta_williams'")['user_id']
    
    attendance_count = 0
    for day_offset in range(5):
        date = (today - timedelta(days=day_offset)).isoformat()
        for student_id in range(1, 6):
            for course_id in [1, 2]:  # CS101 and CS201
                status = statuses[(student_id + day_offset + course_id) % len(statuses)]
                db.execute("""
                    INSERT INTO ATTENDANCE (student_id, course_id, attendance_date, status, recorded_by)
                    VALUES (?, ?, ?, ?, ?)
                """, (student_id, course_id, date, status, ta_user))
                attendance_count += 1
    
    db.commit()
    print(f"    ✓ Created {attendance_count} attendance records")
    
    # =====================================
    # Create Sample Role Requests
    # =====================================
    print("  📝 Creating sample role requests...")
    
    student1_user = db.fetch_one("SELECT user_id FROM USERS WHERE username = 'student1'")['user_id']
    
    db.execute("""
        INSERT INTO ROLE_REQUESTS (user_id, username, current_role, requested_role, reason, comments, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (student1_user, 'student1', 'Student', 'TA', 
          'I have been assisting Professor Smith with grading and would like to become an official TA.',
          'I have strong programming skills and 3.8 GPA.', 'Pending'))
    
    db.commit()
    print("    ✓ Created sample role request")
    
    # =====================================
    # Create Enrollments
    # =====================================
    print("  📝 Creating student enrollments...")
    
    enrollments = [
        # All students in CS101
        (1, 1), (2, 1), (3, 1), (4, 1), (5, 1),
        # Some students in CS201
        (1, 2), (2, 2), (3, 2), (4, 2),
        # Some students in IS301
        (2, 3), (3, 3), (5, 3),
    ]
    
    for student_id, course_id in enrollments:
        try:
            db.execute("""
                INSERT INTO ENROLLMENT (student_id, course_id)
                VALUES (?, ?)
            """, (student_id, course_id))
        except:
            pass
    
    db.commit()
    print(f"    ✓ Created {len(enrollments)} enrollments")
    
    # =====================================
    # Create Announcements
    # =====================================
    print("  📢 Creating announcements...")
    
    admin_user = db.fetch_one("SELECT user_id FROM USERS WHERE username = 'admin'")['user_id']
    
    announcements = [
        (None, 'Welcome to Fall 2024 Semester!', 
         'Welcome all students and staff to the new semester. Please review your course schedules.',
         admin_user, True, 'all'),
        (1, 'CS101 Office Hours Updated',
         'Office hours are now Monday and Wednesday 2-4 PM in Room 305.',
         prof1, False, 'students'),
        (2, 'CS201 Project Due Date Extended',
         'The database security project deadline has been extended by one week.',
         prof1, True, 'students'),
        (None, 'System Maintenance Notice',
         'The system will undergo maintenance this weekend. Expect brief downtime Saturday 2-4 AM.',
         admin_user, True, 'all'),
    ]
    
    for course_id, title, content, author_id, is_pinned, visibility in announcements:
        db.execute("""
            INSERT INTO ANNOUNCEMENTS (course_id, title, content, author_id, is_pinned, visibility)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (course_id, title, content, author_id, 1 if is_pinned else 0, visibility))
    
    db.commit()
    print(f"    ✓ Created {len(announcements)} announcements")
    
    # =====================================
    # Create Sample Notifications
    # =====================================
    print("  🔔 Creating notifications...")
    
    notifications = [
        (student1_user, 'Grade Posted', 'Your grade for CS101 has been posted.', 'success'),
        (student1_user, 'New Announcement', 'New announcement in CS201 course.', 'info'),
        (student1_user, 'Role Request Status', 'Your TA role request is pending admin review.', 'warning'),
        (ta1, 'Attendance Reminder', 'Remember to record attendance for today\'s CS101 class.', 'info'),
        (prof1, 'Unpublished Grades', 'You have 2 unpublished grades in CS201.', 'warning'),
    ]
    
    for user_id, title, message, notif_type in notifications:
        db.execute("""
            INSERT INTO NOTIFICATIONS (user_id, title, message, notification_type)
            VALUES (?, ?, ?, ?)
        """, (user_id, title, message, notif_type))
    
    db.commit()
    print(f"    ✓ Created {len(notifications)} notifications")
    
    print("\n✅ Database seeding complete!")
    print("\n📋 Test Accounts:")
    print("   ┌────────────────┬─────────────┬─────────────┬───────────┐")
    print("   │ Username       │ Password    │ Role        │ Clearance │")
    print("   ├────────────────┼─────────────┼─────────────┼───────────┤")
    print("   │ admin          │ admin123    │ Admin       │ 4         │")
    print("   │ prof_smith     │ prof123     │ Instructor  │ 3         │")
    print("   │ ta_williams    │ ta123       │ TA          │ 2         │")
    print("   │ student1       │ student123  │ Student     │ 1         │")
    print("   │ guest          │ guest123    │ Guest       │ 0         │")
    print("   └────────────────┴─────────────┴─────────────┴───────────┘")
    
    print("\n✨ New Features:")
    print("   • 📝 Enrollments: Students enrolled in courses")
    print("   • 📢 Announcements: System and course announcements")
    print("   • 🔔 Notifications: User notification system")


if __name__ == '__main__':
    seed_database()

