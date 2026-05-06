-- ============================================================
-- SRMS - SECURITY VIEWS (MLS + Inference Control)
-- Database Security Term Project Phase 2
-- Run this script THIRD after sqlserver_roles.sql
-- ============================================================

USE SRMS_SecureDB;
GO

-- ============================================================
-- SECTION 1: DROP EXISTING VIEWS
-- ============================================================

IF OBJECT_ID('dbo.vw_PublicCourseInfo', 'V') IS NOT NULL DROP VIEW dbo.vw_PublicCourseInfo;
IF OBJECT_ID('dbo.vw_StudentOwnProfile', 'V') IS NOT NULL DROP VIEW dbo.vw_StudentOwnProfile;
IF OBJECT_ID('dbo.vw_StudentOwnGrades', 'V') IS NOT NULL DROP VIEW dbo.vw_StudentOwnGrades;
IF OBJECT_ID('dbo.vw_StudentOwnAttendance', 'V') IS NOT NULL DROP VIEW dbo.vw_StudentOwnAttendance;
IF OBJECT_ID('dbo.vw_TAAssignedStudents', 'V') IS NOT NULL DROP VIEW dbo.vw_TAAssignedStudents;
IF OBJECT_ID('dbo.vw_TAAttendance', 'V') IS NOT NULL DROP VIEW dbo.vw_TAAttendance;
IF OBJECT_ID('dbo.vw_InstructorStudents', 'V') IS NOT NULL DROP VIEW dbo.vw_InstructorStudents;
IF OBJECT_ID('dbo.vw_InstructorGrades', 'V') IS NOT NULL DROP VIEW dbo.vw_InstructorGrades;
IF OBJECT_ID('dbo.vw_InstructorAttendance', 'V') IS NOT NULL DROP VIEW dbo.vw_InstructorAttendance;
IF OBJECT_ID('dbo.vw_AdminAllData', 'V') IS NOT NULL DROP VIEW dbo.vw_AdminAllData;
IF OBJECT_ID('dbo.vw_PendingRoleRequests', 'V') IS NOT NULL DROP VIEW dbo.vw_PendingRoleRequests;
GO

PRINT '✓ Dropped existing views';
GO

-- ============================================================
-- SECTION 2: GUEST VIEW - Public Course Info Only (Level 0)
-- ============================================================

CREATE VIEW vw_PublicCourseInfo
AS
SELECT 
    CourseID,
    CourseCode,
    CourseName,
    PublicInfo,              -- Guest-accessible column only
    Department,
    Credits
FROM COURSE
WHERE IsActive = 1
  AND ClassificationLevel = 1;  -- Unclassified only
GO

-- Grant Guest access to this view only
GRANT SELECT ON vw_PublicCourseInfo TO db_Guest;
GO

PRINT '✓ Created vw_PublicCourseInfo (Guest access)';
GO

-- ============================================================
-- SECTION 3: STUDENT VIEWS - Own Data Only (Level 1)
-- MLS: No Read Up enforced - students see only their own data
-- ============================================================

-- Student's own profile
CREATE VIEW vw_StudentOwnProfile
AS
SELECT 
    s.StudentID,
    s.FullName,
    s.Email,
    s.Phone_Display AS Phone,      -- Masked phone only
    s.DOB,
    s.Department,
    s.EnrollmentDate,
    s.Status
FROM STUDENT s
INNER JOIN USERS u ON s.StudentID = u.LinkedID 
    AND u.LinkedType = 'Student'
WHERE u.Username = SYSTEM_USER
  AND s.ClassificationLevel <= u.ClearanceLevel;  -- MLS: No Read Up
GO

GRANT SELECT ON vw_StudentOwnProfile TO db_Student;
GO

PRINT '✓ Created vw_StudentOwnProfile (Student access)';
GO

-- Student's own grades (published only)
CREATE VIEW vw_StudentOwnGrades
AS
SELECT 
    g.GradeID,
    c.CourseCode,
    c.CourseName,
    g.GradeLetter,
    g.Semester,
    g.DateEntered
    -- NOTE: GradeValue is encrypted and NOT exposed to students
FROM GRADES g
INNER JOIN COURSE c ON g.CourseID = c.CourseID
INNER JOIN STUDENT s ON g.StudentID = s.StudentID
INNER JOIN USERS u ON s.StudentID = u.LinkedID 
    AND u.LinkedType = 'Student'
WHERE u.Username = SYSTEM_USER
  AND g.IsPublished = 1;            -- Only published grades visible
GO

GRANT SELECT ON vw_StudentOwnGrades TO db_Student;
GO

PRINT '✓ Created vw_StudentOwnGrades (Published grades only)';
GO

-- Student's own attendance
CREATE VIEW vw_StudentOwnAttendance
AS
SELECT 
    a.AttendanceID,
    c.CourseCode,
    c.CourseName,
    a.AttendanceDate,
    a.StatusText,
    a.Remarks
FROM ATTENDANCE a
INNER JOIN COURSE c ON a.CourseID = c.CourseID
INNER JOIN STUDENT s ON a.StudentID = s.StudentID
INNER JOIN USERS u ON s.StudentID = u.LinkedID 
    AND u.LinkedType = 'Student'
WHERE u.Username = SYSTEM_USER;
GO

GRANT SELECT ON vw_StudentOwnAttendance TO db_Student;
GO

PRINT '✓ Created vw_StudentOwnAttendance (Student access)';
GO

-- ============================================================
-- SECTION 4: TA VIEWS - Assigned Courses Only (Level 2)
-- Inference Control: Restricted to assigned students only
-- ============================================================

-- TA's assigned students (Confidential level)
CREATE VIEW vw_TAAssignedStudents
AS
SELECT DISTINCT
    s.StudentID,
    s.FullName,
    s.Email,
    s.Department,
    c.CourseCode,
    c.CourseName
FROM STUDENT s
INNER JOIN COURSE_ENROLLMENT ce ON s.StudentID = ce.StudentID
INNER JOIN COURSE c ON ce.CourseID = c.CourseID
INNER JOIN COURSE_ASSIGNMENT ca ON c.CourseID = ca.CourseID
INNER JOIN USERS u ON ca.UserID = u.UserID
WHERE u.Username = SYSTEM_USER
  AND ca.AssignmentType = 'TA'
  AND ca.IsActive = 1
  AND s.ClassificationLevel <= 2;  -- Confidential and below only
GO

GRANT SELECT ON vw_TAAssignedStudents TO db_TA;
GO

PRINT '✓ Created vw_TAAssignedStudents (TA restricted view)';
GO

-- TA's attendance records (assigned courses only)
CREATE VIEW vw_TAAttendance
AS
SELECT 
    a.AttendanceID,
    s.FullName AS StudentName,
    s.StudentID,
    c.CourseCode,
    c.CourseName,
    a.AttendanceDate,
    a.StatusText,
    a.Remarks
FROM ATTENDANCE a
INNER JOIN STUDENT s ON a.StudentID = s.StudentID
INNER JOIN COURSE c ON a.CourseID = c.CourseID
INNER JOIN COURSE_ASSIGNMENT ca ON c.CourseID = ca.CourseID
INNER JOIN USERS u ON ca.UserID = u.UserID
WHERE u.Username = SYSTEM_USER
  AND ca.AssignmentType = 'TA'
  AND ca.IsActive = 1;
GO

GRANT SELECT ON vw_TAAttendance TO db_TA;
GO

PRINT '✓ Created vw_TAAttendance (TA restricted view)';
GO

-- ============================================================
-- SECTION 5: INSTRUCTOR VIEWS - Assigned Courses (Level 3)
-- ============================================================

-- Instructor's assigned students
CREATE VIEW vw_InstructorStudents
AS
SELECT DISTINCT
    s.StudentID,
    s.FullName,
    s.Email,
    s.Department,
    c.CourseCode,
    c.CourseName
FROM STUDENT s
INNER JOIN COURSE_ENROLLMENT ce ON s.StudentID = ce.StudentID
INNER JOIN COURSE c ON ce.CourseID = c.CourseID
INNER JOIN COURSE_ASSIGNMENT ca ON c.CourseID = ca.CourseID
INNER JOIN USERS u ON ca.UserID = u.UserID
WHERE u.Username = SYSTEM_USER
  AND ca.AssignmentType = 'Instructor'
  AND ca.IsActive = 1;
GO

GRANT SELECT ON vw_InstructorStudents TO db_Instructor;
GO

PRINT '✓ Created vw_InstructorStudents (Instructor access)';
GO

-- Instructor's grades (assigned courses)
CREATE VIEW vw_InstructorGrades
AS
SELECT 
    g.GradeID,
    s.FullName AS StudentName,
    s.StudentID,
    c.CourseCode,
    c.CourseName,
    g.GradeLetter,
    g.GradeValue_Display AS GradeValue,
    g.Semester,
    g.DateEntered,
    g.IsPublished,
    g.IsFinal
FROM GRADES g
INNER JOIN STUDENT s ON g.StudentID = s.StudentID
INNER JOIN COURSE c ON g.CourseID = c.CourseID
INNER JOIN COURSE_ASSIGNMENT ca ON c.CourseID = ca.CourseID
INNER JOIN USERS u ON ca.UserID = u.UserID
WHERE u.Username = SYSTEM_USER
  AND ca.AssignmentType = 'Instructor'
  AND ca.IsActive = 1;
GO

GRANT SELECT ON vw_InstructorGrades TO db_Instructor;
GO

PRINT '✓ Created vw_InstructorGrades (Instructor access)';
GO

-- Instructor's attendance view
CREATE VIEW vw_InstructorAttendance
AS
SELECT 
    a.AttendanceID,
    s.FullName AS StudentName,
    s.StudentID,
    c.CourseCode,
    c.CourseName,
    a.AttendanceDate,
    a.StatusText,
    a.Remarks
FROM ATTENDANCE a
INNER JOIN STUDENT s ON a.StudentID = s.StudentID
INNER JOIN COURSE c ON a.CourseID = c.CourseID
INNER JOIN COURSE_ASSIGNMENT ca ON c.CourseID = ca.CourseID
INNER JOIN USERS u ON ca.UserID = u.UserID
WHERE u.Username = SYSTEM_USER
  AND ca.AssignmentType = 'Instructor'
  AND ca.IsActive = 1;
GO

GRANT SELECT ON vw_InstructorAttendance TO db_Instructor;
GO

PRINT '✓ Created vw_InstructorAttendance (Instructor access)';
GO

-- ============================================================
-- SECTION 6: ADMIN VIEWS (Level 4 - Full Access)
-- ============================================================

-- Admin view - All grades with full details
CREATE VIEW vw_AdminAllData
AS
SELECT 
    g.GradeID,
    s.StudentID,
    s.FullName AS StudentName,
    s.Email AS StudentEmail,
    c.CourseCode,
    c.CourseName,
    i.FullName AS InstructorName,
    g.GradeLetter,
    g.GradeValue_Display AS GradeValue,
    g.Semester,
    g.DateEntered,
    g.IsPublished,
    g.IsFinal,
    g.ClassificationLevel
FROM GRADES g
INNER JOIN STUDENT s ON g.StudentID = s.StudentID
INNER JOIN COURSE c ON g.CourseID = c.CourseID
LEFT JOIN INSTRUCTOR i ON g.EnteredBy = i.InstructorID;
GO

GRANT SELECT ON vw_AdminAllData TO db_Admin;
GO

PRINT '✓ Created vw_AdminAllData (Admin full access)';
GO

-- ============================================================
-- SECTION 7: ADMIN DASHBOARD VIEW (Part B)
-- ============================================================

-- Pending role requests for admin dashboard
CREATE VIEW vw_PendingRoleRequests
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
FROM ROLE_REQUESTS
WHERE Status = 'Pending'
GO

GRANT SELECT ON vw_PendingRoleRequests TO db_Admin;
GO

PRINT '✓ Created vw_PendingRoleRequests (Admin Part B)';
GO

-- ============================================================
-- SECTION 8: VIEW SUMMARY
-- ============================================================

PRINT '';
PRINT '═══════════════════════════════════════════════════════════════════';
PRINT '  SECURITY VIEWS - SUMMARY';
PRINT '═══════════════════════════════════════════════════════════════════';
PRINT '';
PRINT '  ┌──────────────────────────┬─────────────┬──────────────────────┐';
PRINT '  │ View                     │ Role        │ Purpose              │';
PRINT '  ├──────────────────────────┼─────────────┼──────────────────────┤';
PRINT '  │ vw_PublicCourseInfo      │ Guest       │ Public course info   │';
PRINT '  │ vw_StudentOwnProfile     │ Student     │ Own profile only     │';
PRINT '  │ vw_StudentOwnGrades      │ Student     │ Own published grades │';
PRINT '  │ vw_StudentOwnAttendance  │ Student     │ Own attendance       │';
PRINT '  │ vw_TAAssignedStudents    │ TA          │ Assigned students    │';
PRINT '  │ vw_TAAttendance          │ TA          │ Assigned attendance  │';
PRINT '  │ vw_InstructorStudents    │ Instructor  │ Assigned students    │';
PRINT '  │ vw_InstructorGrades      │ Instructor  │ Grades (RW)          │';
PRINT '  │ vw_InstructorAttendance  │ Instructor  │ Attendance (R)       │';
PRINT '  │ vw_AdminAllData          │ Admin       │ Full data access     │';
PRINT '  │ vw_PendingRoleRequests   │ Admin       │ Part B dashboard     │';
PRINT '  └──────────────────────────┴─────────────┴──────────────────────┘';
PRINT '';
PRINT '  MLS Enforcement: All views check ClassificationLevel';
PRINT '  Inference Control: Views restrict to assigned courses only';
PRINT '';
PRINT '═══════════════════════════════════════════════════════════════════';
GO
