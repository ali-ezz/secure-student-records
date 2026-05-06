-- ============================================================
-- SRMS - COMPLETE SQL SERVER DATABASE SCHEMA
-- Database Security Term Project Phase 2
-- Run this script FIRST in SRMS_SecureDB
-- ============================================================

USE SRMS_SecureDB;
GO

-- ============================================================
-- SECTION 1: CLEAN UP EXISTING OBJECTS (if any)
-- ============================================================
-- Drop existing tables in dependency order
IF OBJECT_ID('dbo.AUDIT_LOG', 'U') IS NOT NULL DROP TABLE dbo.AUDIT_LOG;
IF OBJECT_ID('dbo.ROLE_REQUESTS', 'U') IS NOT NULL DROP TABLE dbo.ROLE_REQUESTS;
IF OBJECT_ID('dbo.ATTENDANCE', 'U') IS NOT NULL DROP TABLE dbo.ATTENDANCE;
IF OBJECT_ID('dbo.GRADES', 'U') IS NOT NULL DROP TABLE dbo.GRADES;
IF OBJECT_ID('dbo.COURSE_ENROLLMENT', 'U') IS NOT NULL DROP TABLE dbo.COURSE_ENROLLMENT;
IF OBJECT_ID('dbo.COURSE_ASSIGNMENT', 'U') IS NOT NULL DROP TABLE dbo.COURSE_ASSIGNMENT;
IF OBJECT_ID('dbo.COURSE', 'U') IS NOT NULL DROP TABLE dbo.COURSE;
IF OBJECT_ID('dbo.STUDENT', 'U') IS NOT NULL DROP TABLE dbo.STUDENT;
IF OBJECT_ID('dbo.INSTRUCTOR', 'U') IS NOT NULL DROP TABLE dbo.INSTRUCTOR;
IF OBJECT_ID('dbo.USERS', 'U') IS NOT NULL DROP TABLE dbo.USERS;
IF OBJECT_ID('dbo.SECURITY_CLASSIFICATION', 'U') IS NOT NULL DROP TABLE dbo.SECURITY_CLASSIFICATION;
GO

PRINT '✓ Cleaned up existing objects';
GO

-- ============================================================
-- SECTION 2: ENCRYPTION SETUP (AES-256)
-- ============================================================

-- Create Master Key (if not exists)
IF NOT EXISTS (SELECT * FROM sys.symmetric_keys WHERE name = '##MS_DatabaseMasterKey##')
BEGIN
    CREATE MASTER KEY ENCRYPTION BY PASSWORD = 'SRMS_MasterKey_2024!@#$';
    PRINT '✓ Master Key created';
END
ELSE
    PRINT '✓ Master Key already exists';
GO

-- Create Certificate for encryption
IF NOT EXISTS (SELECT * FROM sys.certificates WHERE name = 'SRMS_Certificate')
BEGIN
    CREATE CERTIFICATE SRMS_Certificate
    WITH SUBJECT = 'SRMS Data Encryption Certificate',
    EXPIRY_DATE = '2030-12-31';
    PRINT '✓ Certificate created';
END
ELSE
    PRINT '✓ Certificate already exists';
GO

-- Create Symmetric Key (AES_256)
IF NOT EXISTS (SELECT * FROM sys.symmetric_keys WHERE name = 'SRMS_SymmetricKey')
BEGIN
    CREATE SYMMETRIC KEY SRMS_SymmetricKey
    WITH ALGORITHM = AES_256
    ENCRYPTION BY CERTIFICATE SRMS_Certificate;
    PRINT '✓ Symmetric Key (AES_256) created';
END
ELSE
    PRINT '✓ Symmetric Key already exists';
GO

-- ============================================================
-- SECTION 3: SECURITY CLASSIFICATION TABLE
-- ============================================================

CREATE TABLE SECURITY_CLASSIFICATION (
    ClassificationID INT PRIMARY KEY,
    ClassificationName NVARCHAR(50) NOT NULL,
    NumericLevel INT NOT NULL,
    Description NVARCHAR(200)
);

INSERT INTO SECURITY_CLASSIFICATION VALUES 
(0, 'Public', 0, 'Guest accessible, no restrictions'),
(1, 'Unclassified', 1, 'Course information'),
(2, 'Confidential', 2, 'Student/Instructor profiles'),
(3, 'Secret', 3, 'Grades, Attendance records'),
(4, 'Top Secret', 4, 'Disciplinary records, Admin only');

PRINT '✓ Security Classification table created';
GO

-- ============================================================
-- SECTION 4: USERS TABLE (Authentication)
-- ============================================================

CREATE TABLE USERS (
    UserID INT IDENTITY(1,1) PRIMARY KEY,
    Username NVARCHAR(50) NOT NULL UNIQUE,
    Username_Encrypted VARBINARY(256),              -- AES Encrypted
    PasswordHash VARBINARY(256) NOT NULL,           -- Hashed + Encrypted
    PasswordSalt VARBINARY(128) NOT NULL,
    Role NVARCHAR(20) NOT NULL CHECK (Role IN ('Admin', 'Instructor', 'TA', 'Student', 'Guest')),
    ClearanceLevel INT NOT NULL DEFAULT 0 CHECK (ClearanceLevel BETWEEN 0 AND 4),
    LinkedID INT NULL,                               -- FK to Student/Instructor
    LinkedType NVARCHAR(20) NULL CHECK (LinkedType IN ('Student', 'Instructor', 'TA', NULL)),
    IsActive BIT DEFAULT 1,
    IsLocked BIT DEFAULT 0,
    FailedLoginAttempts INT DEFAULT 0,
    LastLoginDate DATETIME NULL,
    CreatedDate DATETIME DEFAULT GETDATE(),
    ModifiedDate DATETIME NULL,
    ModifiedBy NVARCHAR(50) NULL
);

CREATE INDEX IX_Users_Username ON USERS(Username);
CREATE INDEX IX_Users_Role ON USERS(Role);
CREATE INDEX IX_Users_ClearanceLevel ON USERS(ClearanceLevel);

PRINT '✓ USERS table created';
GO

-- ============================================================
-- SECTION 5: INSTRUCTOR TABLE (Classification: Confidential)
-- ============================================================

CREATE TABLE INSTRUCTOR (
    InstructorID INT IDENTITY(1,1) PRIMARY KEY,
    FullName NVARCHAR(100) NOT NULL,
    Email NVARCHAR(100) NOT NULL UNIQUE,
    Phone VARBINARY(256) NULL,                       -- AES Encrypted
    Phone_Display NVARCHAR(20) NULL,                 -- Masked display
    Department NVARCHAR(50),
    Title NVARCHAR(50),
    ClearanceLevel INT DEFAULT 3,                    -- Secret level
    ClassificationLevel INT DEFAULT 2,               -- Confidential
    IsActive BIT DEFAULT 1,
    CreatedDate DATETIME DEFAULT GETDATE()
);

CREATE INDEX IX_Instructor_Email ON INSTRUCTOR(Email);
CREATE INDEX IX_Instructor_ClearanceLevel ON INSTRUCTOR(ClearanceLevel);

PRINT '✓ INSTRUCTOR table created (Confidential)';
GO

-- ============================================================
-- SECTION 6: STUDENT TABLE (Classification: Confidential)
-- ============================================================

CREATE TABLE STUDENT (
    StudentID INT IDENTITY(1,1) PRIMARY KEY,
    StudentID_Encrypted VARBINARY(256) NULL,         -- AES Encrypted
    FullName NVARCHAR(100) NOT NULL,
    Email NVARCHAR(100) NOT NULL UNIQUE,
    Phone VARBINARY(256) NULL,                       -- AES Encrypted
    Phone_Display NVARCHAR(20) NULL,                 -- Masked display
    DOB DATE NULL,
    Department NVARCHAR(50),
    EnrollmentDate DATE DEFAULT GETDATE(),
    Status NVARCHAR(20) DEFAULT 'Active' CHECK (Status IN ('Active', 'Inactive', 'Graduated', 'Suspended')),
    ClearanceLevel INT DEFAULT 1,                    -- Unclassified level
    ClassificationLevel INT DEFAULT 2,               -- Confidential
    CreatedDate DATETIME DEFAULT GETDATE()
);

CREATE INDEX IX_Student_Email ON STUDENT(Email);
CREATE INDEX IX_Student_Department ON STUDENT(Department);
CREATE INDEX IX_Student_ClearanceLevel ON STUDENT(ClearanceLevel);

PRINT '✓ STUDENT table created (Confidential)';
GO

-- ============================================================
-- SECTION 7: COURSE TABLE (Classification: Unclassified)
-- ============================================================

CREATE TABLE COURSE (
    CourseID INT IDENTITY(1,1) PRIMARY KEY,
    CourseCode NVARCHAR(20) NOT NULL UNIQUE,
    CourseName NVARCHAR(100) NOT NULL,
    Description NVARCHAR(MAX) NULL,
    PublicInfo NVARCHAR(MAX) NULL,                   -- Guest accessible
    Credits INT DEFAULT 3,
    Department NVARCHAR(50),
    Semester NVARCHAR(20),
    Year INT,
    MaxCapacity INT DEFAULT 30,
    InstructorID INT NULL REFERENCES INSTRUCTOR(InstructorID),
    ClassificationLevel INT DEFAULT 1,               -- Unclassified
    IsActive BIT DEFAULT 1,
    CreatedDate DATETIME DEFAULT GETDATE()
);

CREATE INDEX IX_Course_Code ON COURSE(CourseCode);
CREATE INDEX IX_Course_Department ON COURSE(Department);
CREATE INDEX IX_Course_InstructorID ON COURSE(InstructorID);

PRINT '✓ COURSE table created (Unclassified)';
GO

-- ============================================================
-- SECTION 8: GRADES TABLE (Classification: Secret)
-- ============================================================

CREATE TABLE GRADES (
    GradeID INT IDENTITY(1,1) PRIMARY KEY,
    StudentID INT NOT NULL REFERENCES STUDENT(StudentID),
    StudentID_Encrypted VARBINARY(256) NULL,         -- AES Encrypted
    CourseID INT NOT NULL REFERENCES COURSE(CourseID),
    GradeValue VARBINARY(256) NULL,                  -- AES Encrypted (actual grade)
    GradeValue_Display DECIMAL(5,2) NULL,            -- For aggregates only
    GradeLetter NVARCHAR(2) NULL,
    Semester NVARCHAR(20),
    DateEntered DATETIME DEFAULT GETDATE(),
    EnteredBy INT NULL REFERENCES INSTRUCTOR(InstructorID),
    IsPublished BIT DEFAULT 0,                       -- Student can only see if published
    IsFinal BIT DEFAULT 0,
    ClassificationLevel INT DEFAULT 3,               -- Secret
    CreatedDate DATETIME DEFAULT GETDATE()
);

CREATE INDEX IX_Grades_StudentID ON GRADES(StudentID);
CREATE INDEX IX_Grades_CourseID ON GRADES(CourseID);
CREATE INDEX IX_Grades_IsPublished ON GRADES(IsPublished);

PRINT '✓ GRADES table created (Secret)';
GO

-- ============================================================
-- SECTION 9: ATTENDANCE TABLE (Classification: Secret)
-- ============================================================

CREATE TABLE ATTENDANCE (
    AttendanceID INT IDENTITY(1,1) PRIMARY KEY,
    StudentID INT NOT NULL REFERENCES STUDENT(StudentID),
    CourseID INT NOT NULL REFERENCES COURSE(CourseID),
    AttendanceDate DATE NOT NULL,
    Status BIT NOT NULL DEFAULT 1,                   -- 1 = Present, 0 = Absent
    StatusText AS (CASE WHEN Status = 1 THEN 'Present' ELSE 'Absent' END),
    Remarks NVARCHAR(200) NULL,
    RecordedBy INT NULL,                             -- UserID who recorded
    ClassificationLevel INT DEFAULT 3,               -- Secret
    CreatedDate DATETIME DEFAULT GETDATE()
);

CREATE INDEX IX_Attendance_StudentID ON ATTENDANCE(StudentID);
CREATE INDEX IX_Attendance_CourseID ON ATTENDANCE(CourseID);
CREATE INDEX IX_Attendance_Date ON ATTENDANCE(AttendanceDate);

PRINT '✓ ATTENDANCE table created (Secret)';
GO

-- ============================================================
-- SECTION 10: COURSE ENROLLMENT TABLE
-- ============================================================

CREATE TABLE COURSE_ENROLLMENT (
    EnrollmentID INT IDENTITY(1,1) PRIMARY KEY,
    StudentID INT NOT NULL REFERENCES STUDENT(StudentID),
    CourseID INT NOT NULL REFERENCES COURSE(CourseID),
    EnrollmentDate DATE DEFAULT GETDATE(),
    Status NVARCHAR(20) DEFAULT 'Enrolled' CHECK (Status IN ('Enrolled', 'Dropped', 'Completed')),
    Semester NVARCHAR(20),
    Year INT,
    CONSTRAINT UQ_StudentCourse UNIQUE (StudentID, CourseID, Semester, Year)
);

CREATE INDEX IX_Enrollment_StudentID ON COURSE_ENROLLMENT(StudentID);
CREATE INDEX IX_Enrollment_CourseID ON COURSE_ENROLLMENT(CourseID);

PRINT '✓ COURSE_ENROLLMENT table created';
GO

-- ============================================================
-- SECTION 11: COURSE ASSIGNMENT TABLE (Instructor/TA assignments)
-- ============================================================

CREATE TABLE COURSE_ASSIGNMENT (
    AssignmentID INT IDENTITY(1,1) PRIMARY KEY,
    CourseID INT NOT NULL REFERENCES COURSE(CourseID),
    UserID INT NOT NULL REFERENCES USERS(UserID),
    AssignmentType NVARCHAR(20) NOT NULL CHECK (AssignmentType IN ('Instructor', 'TA')),
    Semester NVARCHAR(20),
    Year INT,
    IsActive BIT DEFAULT 1,
    AssignedDate DATETIME DEFAULT GETDATE(),
    CONSTRAINT UQ_CourseUserAssignment UNIQUE (CourseID, UserID, Semester, Year)
);

CREATE INDEX IX_Assignment_CourseID ON COURSE_ASSIGNMENT(CourseID);
CREATE INDEX IX_Assignment_UserID ON COURSE_ASSIGNMENT(UserID);

PRINT '✓ COURSE_ASSIGNMENT table created';
GO

-- ============================================================
-- SECTION 12: ROLE REQUESTS TABLE (Part B)
-- ============================================================

CREATE TABLE ROLE_REQUESTS (
    RequestID INT IDENTITY(1,1) PRIMARY KEY,
    UserID INT NOT NULL REFERENCES USERS(UserID),
    Username NVARCHAR(50) NOT NULL,
    CurrentRole NVARCHAR(20) NOT NULL,
    RequestedRole NVARCHAR(20) NOT NULL CHECK (RequestedRole IN ('TA', 'Instructor')),
    CurrentClearance INT NOT NULL,
    RequestedClearance INT NOT NULL,
    Reason NVARCHAR(MAX) NOT NULL,
    Comments NVARCHAR(MAX) NULL,
    Status NVARCHAR(20) DEFAULT 'Pending' CHECK (Status IN ('Pending', 'Approved', 'Denied')),
    DateSubmitted DATETIME DEFAULT GETDATE(),
    DateProcessed DATETIME NULL,
    ProcessedBy INT NULL REFERENCES USERS(UserID),
    ProcessedByUsername NVARCHAR(50) NULL,
    AdminComments NVARCHAR(MAX) NULL
);

CREATE INDEX IX_RoleRequests_UserID ON ROLE_REQUESTS(UserID);
CREATE INDEX IX_RoleRequests_Status ON ROLE_REQUESTS(Status);

PRINT '✓ ROLE_REQUESTS table created (Part B)';
GO

-- ============================================================
-- SECTION 13: AUDIT LOG TABLE
-- ============================================================

CREATE TABLE AUDIT_LOG (
    LogID INT IDENTITY(1,1) PRIMARY KEY,
    ActionType NVARCHAR(50) NOT NULL,
    TableName NVARCHAR(50) NULL,
    RecordID INT NULL,
    UserID INT NULL,
    Username NVARCHAR(50) NULL,
    UserRole NVARCHAR(20) NULL,
    UserClearance INT NULL,
    DataClassification INT NULL,
    AccessGranted BIT NULL,
    Description NVARCHAR(MAX) NULL,
    OldValues NVARCHAR(MAX) NULL,
    NewValues NVARCHAR(MAX) NULL,
    IPAddress NVARCHAR(50) NULL,
    ActionDate DATETIME DEFAULT GETDATE()
);

CREATE INDEX IX_AuditLog_ActionType ON AUDIT_LOG(ActionType);
CREATE INDEX IX_AuditLog_UserID ON AUDIT_LOG(UserID);
CREATE INDEX IX_AuditLog_ActionDate ON AUDIT_LOG(ActionDate);

PRINT '✓ AUDIT_LOG table created';
GO

-- ============================================================
-- SECTION 14: DATABASE SCHEMA SUMMARY
-- ============================================================

PRINT '';
PRINT '═══════════════════════════════════════════════════════════';
PRINT '  SRMS DATABASE SCHEMA - CREATION COMPLETE';
PRINT '═══════════════════════════════════════════════════════════';
PRINT '';
PRINT '  Tables Created:';
PRINT '  ───────────────────────────────────────────────────────';
PRINT '  │ Table                  │ Classification │ Encrypted │';
PRINT '  ├────────────────────────┼────────────────┼───────────┤';
PRINT '  │ SECURITY_CLASSIFICATION│ N/A            │ No        │';
PRINT '  │ USERS                  │ N/A            │ Yes (2)   │';
PRINT '  │ INSTRUCTOR             │ Confidential   │ Yes (1)   │';
PRINT '  │ STUDENT                │ Confidential   │ Yes (2)   │';
PRINT '  │ COURSE                 │ Unclassified   │ No        │';
PRINT '  │ GRADES                 │ Secret         │ Yes (2)   │';
PRINT '  │ ATTENDANCE             │ Secret         │ No        │';
PRINT '  │ COURSE_ENROLLMENT      │ N/A            │ No        │';
PRINT '  │ COURSE_ASSIGNMENT      │ N/A            │ No        │';
PRINT '  │ ROLE_REQUESTS          │ N/A            │ No        │';
PRINT '  │ AUDIT_LOG              │ N/A            │ No        │';
PRINT '  ───────────────────────────────────────────────────────';
PRINT '';
PRINT '  Encryption:';
PRINT '  • Master Key: Created ✓';
PRINT '  • Certificate: SRMS_Certificate ✓';
PRINT '  • Symmetric Key: SRMS_SymmetricKey (AES_256) ✓';
PRINT '';
PRINT '═══════════════════════════════════════════════════════════';
GO
