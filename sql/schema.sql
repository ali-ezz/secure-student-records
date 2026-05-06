-- ============================================
-- SRMS - Secure Student Records Management System
-- Database Schema (SQL Server Compatible)
-- ============================================

-- Drop tables if exist (for clean setup)
DROP TABLE IF EXISTS ROLE_REQUESTS;
DROP TABLE IF EXISTS ATTENDANCE;
DROP TABLE IF EXISTS GRADES;
DROP TABLE IF EXISTS COURSE_ASSIGNMENTS;
DROP TABLE IF EXISTS COURSE;
DROP TABLE IF EXISTS INSTRUCTOR;
DROP TABLE IF EXISTS STUDENT;
DROP TABLE IF EXISTS USERS;
DROP TABLE IF EXISTS AUDIT_LOG;

-- ============================================
-- USERS TABLE (Authentication)
-- Classification: Top Secret
-- ============================================
CREATE TABLE USERS (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,          -- Encrypted
    password_hash TEXT NOT NULL,            -- Hashed with bcrypt
    salt TEXT NOT NULL,                     -- Password salt
    role TEXT NOT NULL CHECK(role IN ('Admin', 'Instructor', 'TA', 'Student', 'Guest')),
    clearance_level INTEGER NOT NULL DEFAULT 0 CHECK(clearance_level BETWEEN 0 AND 4),
    linked_id INTEGER,                      -- Links to Student/Instructor ID
    is_active INTEGER DEFAULT 1,
    failed_login_attempts INTEGER DEFAULT 0,
    last_login DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- STUDENT TABLE
-- Classification: Confidential (Level 2)
-- ============================================
CREATE TABLE STUDENT (
    student_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id_encrypted TEXT,              -- AES Encrypted
    full_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    phone_encrypted TEXT,                   -- AES Encrypted
    date_of_birth DATE,
    department TEXT,
    clearance_level INTEGER DEFAULT 2,      -- Confidential
    security_classification INTEGER DEFAULT 2,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- INSTRUCTOR TABLE
-- Classification: Confidential (Level 2)
-- ============================================
CREATE TABLE INSTRUCTOR (
    instructor_id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    department TEXT,
    clearance_level INTEGER DEFAULT 3,      -- Secret (can view grades)
    security_classification INTEGER DEFAULT 2,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- COURSE TABLE
-- Classification: Unclassified (Level 1), Public Info (Level 0)
-- ============================================
CREATE TABLE COURSE (
    course_id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_code TEXT NOT NULL UNIQUE,
    course_name TEXT NOT NULL,
    description TEXT,
    public_info TEXT,                       -- Guest visible (Level 0)
    credits INTEGER DEFAULT 3,
    instructor_id INTEGER,
    security_classification INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (instructor_id) REFERENCES INSTRUCTOR(instructor_id)
);

-- ============================================
-- COURSE_ASSIGNMENTS (TA/Instructor to Course mappings)
-- ============================================
CREATE TABLE COURSE_ASSIGNMENTS (
    assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('Instructor', 'TA')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES USERS(user_id),
    FOREIGN KEY (course_id) REFERENCES COURSE(course_id),
    UNIQUE(user_id, course_id)
);

-- ============================================
-- GRADES TABLE
-- Classification: Secret (Level 3)
-- ============================================
CREATE TABLE GRADES (
    grade_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    student_id_encrypted TEXT,              -- AES Encrypted reference
    course_id INTEGER NOT NULL,
    grade_value_encrypted TEXT,             -- AES Encrypted
    grade_letter TEXT,                      -- A, B, C, D, F
    is_published INTEGER DEFAULT 0,         -- Students can only see published grades
    date_entered DATETIME DEFAULT CURRENT_TIMESTAMP,
    entered_by INTEGER,                     -- Instructor user_id
    security_classification INTEGER DEFAULT 3,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES STUDENT(student_id),
    FOREIGN KEY (course_id) REFERENCES COURSE(course_id),
    FOREIGN KEY (entered_by) REFERENCES USERS(user_id)
);

-- ============================================
-- ATTENDANCE TABLE
-- Classification: Secret (Level 3)
-- ============================================
CREATE TABLE ATTENDANCE (
    attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    attendance_date DATE NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('Present', 'Absent', 'Late', 'Excused')),
    recorded_by INTEGER,                    -- TA or Instructor user_id
    security_classification INTEGER DEFAULT 3,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES STUDENT(student_id),
    FOREIGN KEY (course_id) REFERENCES COURSE(course_id),
    FOREIGN KEY (recorded_by) REFERENCES USERS(user_id),
    UNIQUE(student_id, course_id, attendance_date)
);

-- ============================================
-- ROLE_REQUESTS TABLE (Part B)
-- For role upgrade workflow
-- ============================================
CREATE TABLE ROLE_REQUESTS (
    request_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    username TEXT NOT NULL,
    current_role TEXT NOT NULL,
    requested_role TEXT NOT NULL,
    reason TEXT NOT NULL,
    comments TEXT,
    status TEXT DEFAULT 'Pending' CHECK(status IN ('Pending', 'Approved', 'Denied')),
    date_submitted DATETIME DEFAULT CURRENT_TIMESTAMP,
    date_processed DATETIME,
    processed_by TEXT,                      -- Admin username
    admin_comments TEXT,
    FOREIGN KEY (user_id) REFERENCES USERS(user_id)
);

-- ============================================
-- AUDIT_LOG TABLE (Security Tracking)
-- ============================================
CREATE TABLE AUDIT_LOG (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    username TEXT,
    action TEXT NOT NULL,
    table_name TEXT,
    record_id INTEGER,
    old_value TEXT,
    new_value TEXT,
    ip_address TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    security_level INTEGER,
    FOREIGN KEY (user_id) REFERENCES USERS(user_id)
);

-- ============================================
-- INDEXES for Performance
-- ============================================
CREATE INDEX idx_users_username ON USERS(username);
CREATE INDEX idx_users_role ON USERS(role);
CREATE INDEX idx_student_email ON STUDENT(email);
CREATE INDEX idx_grades_student ON GRADES(student_id);
CREATE INDEX idx_grades_course ON GRADES(course_id);
CREATE INDEX idx_attendance_student ON ATTENDANCE(student_id);
CREATE INDEX idx_attendance_course ON ATTENDANCE(course_id);
CREATE INDEX idx_role_requests_status ON ROLE_REQUESTS(status);
CREATE INDEX idx_audit_user ON AUDIT_LOG(user_id);
CREATE INDEX idx_audit_action ON AUDIT_LOG(action);

-- ============================================
-- NOTIFICATIONS TABLE (New Feature)
-- For system alerts and messages
-- ============================================
CREATE TABLE NOTIFICATIONS (
    notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    notification_type TEXT DEFAULT 'info' CHECK(notification_type IN ('info', 'warning', 'success', 'error')),
    is_read INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES USERS(user_id)
);

-- ============================================
-- SESSIONS TABLE (Security Feature)
-- Track active user sessions
-- ============================================
CREATE TABLE SESSIONS (
    session_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    session_token TEXT NOT NULL UNIQUE,
    ip_address TEXT,
    user_agent TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME,
    is_active INTEGER DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES USERS(user_id)
);

-- ============================================
-- ANNOUNCEMENTS TABLE (Communication)
-- Course and system announcements
-- ============================================
CREATE TABLE ANNOUNCEMENTS (
    announcement_id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id INTEGER,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    author_id INTEGER NOT NULL,
    is_pinned INTEGER DEFAULT 0,
    visibility TEXT DEFAULT 'all' CHECK(visibility IN ('all', 'students', 'staff', 'admin')),
    security_classification INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES COURSE(course_id),
    FOREIGN KEY (author_id) REFERENCES USERS(user_id)
);

-- ============================================
-- ENROLLMENT TABLE (Student Course Registration)
-- ============================================
CREATE TABLE ENROLLMENT (
    enrollment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    enrollment_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'active' CHECK(status IN ('active', 'dropped', 'completed')),
    final_grade TEXT,
    FOREIGN KEY (student_id) REFERENCES STUDENT(student_id),
    FOREIGN KEY (course_id) REFERENCES COURSE(course_id),
    UNIQUE(student_id, course_id)
);

-- ============================================
-- SYSTEM_SETTINGS TABLE (Configuration)
-- ============================================
CREATE TABLE SYSTEM_SETTINGS (
    setting_id INTEGER PRIMARY KEY AUTOINCREMENT,
    setting_key TEXT NOT NULL UNIQUE,
    setting_value TEXT,
    setting_type TEXT DEFAULT 'string' CHECK(setting_type IN ('string', 'integer', 'boolean', 'json')),
    description TEXT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_by INTEGER,
    FOREIGN KEY (updated_by) REFERENCES USERS(user_id)
);

-- Default system settings
INSERT INTO SYSTEM_SETTINGS (setting_key, setting_value, setting_type, description) VALUES
('session_timeout_minutes', '30', 'integer', 'Session timeout in minutes'),
('max_login_attempts', '5', 'integer', 'Maximum failed login attempts before lockout'),
('password_min_length', '8', 'integer', 'Minimum password length'),
('require_2fa', 'false', 'boolean', 'Require two-factor authentication'),
('maintenance_mode', 'false', 'boolean', 'System maintenance mode');

-- Additional indexes for new tables
CREATE INDEX idx_notifications_user ON NOTIFICATIONS(user_id);
CREATE INDEX idx_notifications_read ON NOTIFICATIONS(is_read);
CREATE INDEX idx_sessions_user ON SESSIONS(user_id);
CREATE INDEX idx_sessions_active ON SESSIONS(is_active);
CREATE INDEX idx_enrollment_student ON ENROLLMENT(student_id);
CREATE INDEX idx_enrollment_course ON ENROLLMENT(course_id);
CREATE INDEX idx_announcements_course ON ANNOUNCEMENTS(course_id);
