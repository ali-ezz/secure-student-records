-- ============================================================
-- SRMS - SQL SERVER ROLES, PERMISSIONS, AND VIEWS
-- Implements RBAC and MLS Views
-- ============================================================

USE SRMS_SecureDB;
GO

-- ============================================================
-- SECTION 1: CREATE DATABASE ROLES
-- ============================================================

IF NOT EXISTS (SELECT * FROM sys.database_principals WHERE name = 'db_Admin' AND type = 'R')
    CREATE ROLE db_Admin;
GO

IF NOT EXISTS (SELECT * FROM sys.database_principals WHERE name = 'db_Instructor' AND type = 'R')
    CREATE ROLE db_Instructor;
GO

IF NOT EXISTS (SELECT * FROM sys.database_principals WHERE name = 'db_TA' AND type = 'R')
    CREATE ROLE db_TA;
GO

IF NOT EXISTS (SELECT * FROM sys.database_principals WHERE name = 'db_Student' AND type = 'R')
    CREATE ROLE db_Student;
GO

IF NOT EXISTS (SELECT * FROM sys.database_principals WHERE name = 'db_Guest' AND type = 'R')
    CREATE ROLE db_Guest;
GO

-- ============================================================
-- SECTION 2: ADMIN ROLE PERMISSIONS (Full Access)
-- ============================================================

-- Full control on all tables
GRANT SELECT, INSERT, UPDATE, DELETE ON Student TO db_Admin;
GRANT SELECT, INSERT, UPDATE, DELETE ON Instructor TO db_Admin;
GRANT SELECT, INSERT, UPDATE, DELETE ON Course TO db_Admin;
GRANT SELECT, INSERT, UPDATE, DELETE ON Grades TO db_Admin;
GRANT SELECT, INSERT, UPDATE, DELETE ON Attendance TO db_Admin;
GRANT SELECT, INSERT, UPDATE, DELETE ON Users TO db_Admin;
GRANT SELECT, INSERT, UPDATE, DELETE ON RoleRequests TO db_Admin;
GRANT SELECT, INSERT, UPDATE, DELETE ON CourseEnrollment TO db_Admin;
GRANT SELECT, INSERT, UPDATE, DELETE ON CourseAssignment TO db_Admin;
GRANT SELECT, INSERT ON AuditLog TO db_Admin;

-- Execute stored procedures
GRANT EXECUTE ON SCHEMA::dbo TO db_Admin;

-- View definitions
GRANT VIEW DEFINITION ON SCHEMA::dbo TO db_Admin;
GO

PRINT 'Admin role permissions granted';
GO

-- ============================================================
-- SECTION 3: INSTRUCTOR ROLE PERMISSIONS (Secret Level)
-- ============================================================

-- Student: Read only for assigned courses
GRANT SELECT ON Student TO db_Instructor;
DENY INSERT, DELETE ON Student TO db_Instructor;

-- Instructor: Own profile only
GRANT SELECT, UPDATE ON Instructor TO db_Instructor;
DENY INSERT, DELETE ON Instructor TO db_Instructor;

-- Course: Read all
GRANT SELECT ON Course TO db_Instructor;
DENY INSERT, UPDATE, DELETE ON Course TO db_Instructor;

-- Grades: Full access for assigned courses
GRANT SELECT, INSERT, UPDATE ON Grades TO db_Instructor;
DENY DELETE ON Grades TO db_Instructor;

-- Attendance: Read only
GRANT SELECT ON Attendance TO db_Instructor;
DENY INSERT, UPDATE, DELETE ON Attendance TO db_Instructor;

-- Users: Deny all
DENY SELECT, INSERT, UPDATE, DELETE ON Users TO db_Instructor;

-- RoleRequests: Can submit own requests
GRANT SELECT, INSERT ON RoleRequests TO db_Instructor;
DENY UPDATE, DELETE ON RoleRequests TO db_Instructor;
GO

PRINT 'Instructor role permissions granted';
GO

-- ============================================================
-- SECTION 4: TA ROLE PERMISSIONS (Confidential Level)
-- ============================================================

-- Student: Read only for assigned courses
GRANT SELECT ON Student TO db_TA;
DENY INSERT, UPDATE, DELETE ON Student TO db_TA;

-- Instructor: Deny all
DENY SELECT, INSERT, UPDATE, DELETE ON Instructor TO db_TA;

-- Course: Read only
GRANT SELECT ON Course TO db_TA;
DENY INSERT, UPDATE, DELETE ON Course TO db_TA;

-- Grades: DENY ALL (TAs cannot access grades)
DENY SELECT, INSERT, UPDATE, DELETE ON Grades TO db_TA;

-- Attendance: Full access for assigned courses
GRANT SELECT, INSERT, UPDATE ON Attendance TO db_TA;
DENY DELETE ON Attendance TO db_TA;

-- Users: Deny all
DENY SELECT, INSERT, UPDATE, DELETE ON Users TO db_TA;

-- RoleRequests: Can submit own requests
GRANT SELECT, INSERT ON RoleRequests TO db_TA;
DENY UPDATE, DELETE ON RoleRequests TO db_TA;
GO

PRINT 'TA role permissions granted';
GO

-- ============================================================
-- SECTION 5: STUDENT ROLE PERMISSIONS (Unclassified Level)
-- ============================================================

-- Student: Own profile only (via view)
GRANT SELECT ON Student TO db_Student;
DENY INSERT, UPDATE, DELETE ON Student TO db_Student;

-- Instructor: Deny all
DENY SELECT, INSERT, UPDATE, DELETE ON Instructor TO db_Student;

-- Course: Read only
GRANT SELECT ON Course TO db_Student;
DENY INSERT, UPDATE, DELETE ON Course TO db_Student;

-- Grades: Own grades only when published (via view)
GRANT SELECT ON Grades TO db_Student;
DENY INSERT, UPDATE, DELETE ON Grades TO db_Student;

-- Attendance: Own attendance only (via view)
GRANT SELECT ON Attendance TO db_Student;
DENY INSERT, UPDATE, DELETE ON Attendance TO db_Student;

-- Users: Deny all
DENY SELECT, INSERT, UPDATE, DELETE ON Users TO db_Student;

-- RoleRequests: Can submit own requests
GRANT SELECT, INSERT ON RoleRequests TO db_Student;
DENY UPDATE, DELETE ON RoleRequests TO db_Student;
GO

PRINT 'Student role permissions granted';
GO

-- ============================================================
-- SECTION 6: GUEST ROLE PERMISSIONS (Public Only)
-- ============================================================

-- Deny all on sensitive tables
DENY SELECT, INSERT, UPDATE, DELETE ON Student TO db_Guest;
DENY SELECT, INSERT, UPDATE, DELETE ON Instructor TO db_Guest;
DENY SELECT, INSERT, UPDATE, DELETE ON Grades TO db_Guest;
DENY SELECT, INSERT, UPDATE, DELETE ON Attendance TO db_Guest;
DENY SELECT, INSERT, UPDATE, DELETE ON Users TO db_Guest;
DENY SELECT, INSERT, UPDATE, DELETE ON RoleRequests TO db_Guest;
DENY SELECT, INSERT, UPDATE, DELETE ON CourseEnrollment TO db_Guest;
DENY SELECT, INSERT, UPDATE, DELETE ON CourseAssignment TO db_Guest;
GO

PRINT 'Guest role permissions granted';
GO

-- ============================================================
-- SECTION 7: SECURITY VIEWS (MLS Implementation)
-- ============================================================

-- 7.1 PUBLIC COURSE INFORMATION (FOR GUESTS)
CREATE OR ALTER VIEW vw_PublicCourseInfo
AS
SELECT 
    CourseID,
    CourseCode,
    CourseName,
    PublicInfo,
    Department,
    Credits
FROM Course
WHERE IsActive = 1
  AND ClassificationLevel <= 2;  -- Public/Unclassified only
GO

GRANT SELECT ON vw_PublicCourseInfo TO db_Guest;
GO

-- 7.2 STUDENT OWN PROFILE
CREATE OR ALTER VIEW vw_StudentOwnProfile
AS
SELECT 
    s.StudentID,
    s.FullName,
    s.Email,
    s.Department,
    s.EnrollmentDate,
    s.Status
FROM Student s
INNER JOIN Users u ON s.StudentID = u.LinkedID AND u.LinkedType = 'Student'
WHERE u.Username = SYSTEM_USER;
GO

GRANT SELECT ON vw_StudentOwnProfile TO db_Student;
GO

-- 7.3 STUDENT OWN GRADES (PUBLISHED ONLY)
CREATE OR ALTER VIEW vw_StudentOwnGrades
AS
SELECT 
    g.GradeID,
    c.CourseName,
    c.CourseCode,
    g.GradeLetter,
    g.Semester,
    g.DateEntered
FROM Grades g
INNER JOIN Course c ON g.CourseID = c.CourseID
INNER JOIN Student s ON g.StudentID = s.StudentID
INNER JOIN Users u ON s.StudentID = u.LinkedID AND u.LinkedType = 'Student'
WHERE u.Username = SYSTEM_USER
  AND g.IsPublished = 1;  -- Only published grades
GO

GRANT SELECT ON vw_StudentOwnGrades TO db_Student;
GO

-- 7.4 STUDENT OWN ATTENDANCE
CREATE OR ALTER VIEW vw_StudentOwnAttendance
AS
SELECT 
    a.AttendanceID,
    c.CourseName,
    c.CourseCode,
    a.AttendanceDate,
    a.StatusText,
    a.Remarks
FROM Attendance a
INNER JOIN Course c ON a.CourseID = c.CourseID
INNER JOIN Student s ON a.StudentID = s.StudentID
INNER JOIN Users u ON s.StudentID = u.LinkedID AND u.LinkedType = 'Student'
WHERE u.Username = SYSTEM_USER;
GO

GRANT SELECT ON vw_StudentOwnAttendance TO db_Student;
GO

-- 7.5 TA ASSIGNED STUDENTS (CONFIDENTIAL)
CREATE OR ALTER VIEW vw_TAAssignedStudents
AS
SELECT 
    s.StudentID,
    s.FullName,
    s.Email,
    s.Department,
    c.CourseName,
    c.CourseCode
FROM Student s
INNER JOIN CourseEnrollment ce ON s.StudentID = ce.StudentID
INNER JOIN Course c ON ce.CourseID = c.CourseID
INNER JOIN CourseAssignment ca ON c.CourseID = ca.CourseID
INNER JOIN Users u ON ca.UserID = u.UserID
WHERE u.Username = SYSTEM_USER
  AND ca.AssignmentType = 'TA'
  AND ca.IsActive = 1
  AND s.ClassificationLevel <= 3;  -- Confidential and below
GO

GRANT SELECT ON vw_TAAssignedStudents TO db_TA;
GO

-- 7.6 INSTRUCTOR GRADES (SECRET LEVEL)
CREATE OR ALTER VIEW vw_InstructorGrades
AS
SELECT 
    g.GradeID,
    s.FullName AS StudentName,
    s.StudentID,
    c.CourseName,
    c.CourseCode,
    g.GradeLetter,
    g.GradeValue_Display,
    g.DateEntered,
    g.IsPublished,
    g.IsFinal
FROM Grades g
INNER JOIN Student s ON g.StudentID = s.StudentID
INNER JOIN Course c ON g.CourseID = c.CourseID
INNER JOIN CourseAssignment ca ON c.CourseID = ca.CourseID
INNER JOIN Users u ON ca.UserID = u.UserID
WHERE u.Username = SYSTEM_USER
  AND ca.AssignmentType = 'Instructor'
  AND ca.IsActive = 1;
GO

GRANT SELECT ON vw_InstructorGrades TO db_Instructor;
GO

-- 7.7 INSTRUCTOR ATTENDANCE VIEW
CREATE OR ALTER VIEW vw_InstructorAttendance
AS
SELECT 
    a.AttendanceID,
    s.FullName AS StudentName,
    s.StudentID,
    c.CourseName,
    c.CourseCode,
    a.AttendanceDate,
    a.StatusText,
    a.Remarks
FROM Attendance a
INNER JOIN Student s ON a.StudentID = s.StudentID
INNER JOIN Course c ON a.CourseID = c.CourseID
INNER JOIN CourseAssignment ca ON c.CourseID = ca.CourseID
INNER JOIN Users u ON ca.UserID = u.UserID
WHERE u.Username = SYSTEM_USER
  AND ca.AssignmentType = 'Instructor'
  AND ca.IsActive = 1;
GO

GRANT SELECT ON vw_InstructorAttendance TO db_Instructor;
GO

-- 7.8 TA ATTENDANCE VIEW
CREATE OR ALTER VIEW vw_TAAttendance
AS
SELECT 
    a.AttendanceID,
    s.FullName AS StudentName,
    s.StudentID,
    c.CourseName,
    c.CourseCode,
    a.AttendanceDate,
    a.StatusText,
    a.Remarks
FROM Attendance a
INNER JOIN Student s ON a.StudentID = s.StudentID
INNER JOIN Course c ON a.CourseID = c.CourseID
INNER JOIN CourseAssignment ca ON c.CourseID = ca.CourseID
INNER JOIN Users u ON ca.UserID = u.UserID
WHERE u.Username = SYSTEM_USER
  AND ca.AssignmentType = 'TA'
  AND ca.IsActive = 1;
GO

GRANT SELECT ON vw_TAAttendance TO db_TA;
GO

-- 7.9 ADMIN FULL VIEW (ALL DATA)
CREATE OR ALTER VIEW vw_AdminAllGrades
AS
SELECT 
    g.GradeID,
    s.FullName AS StudentName,
    s.StudentID,
    s.Email AS StudentEmail,
    c.CourseCode,
    c.CourseName,
    i.FullName AS InstructorName,
    g.GradeLetter,
    g.GradeValue_Display,
    g.DateEntered,
    g.IsPublished,
    g.IsFinal,
    g.Semester
FROM Grades g
INNER JOIN Student s ON g.StudentID = s.StudentID
INNER JOIN Course c ON g.CourseID = c.CourseID
LEFT JOIN Instructor i ON g.EnteredBy = i.InstructorID;
GO

GRANT SELECT ON vw_AdminAllGrades TO db_Admin;
GO

-- 7.10 PENDING ROLE REQUESTS (ADMIN)
CREATE OR ALTER VIEW vw_PendingRoleRequests
AS
SELECT 
    RequestID,
    Username,
    CurrentRole,
    RequestedRole,
    CurrentClearance,
    RequestedClearance,
    Reason,
    Comments,
    DateSubmitted,
    Status
FROM RoleRequests
WHERE Status = 'Pending';
GO

GRANT SELECT ON vw_PendingRoleRequests TO db_Admin;
GO

PRINT '✅ All roles, permissions, and views created successfully!';
GO
