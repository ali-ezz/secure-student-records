-- ============================================================
-- SRMS - SQL SERVER ROLES AND PERMISSIONS (RBAC)
-- Database Security Term Project Phase 2
-- Run this script SECOND after sqlserver_schema.sql
-- ============================================================

USE SRMS_SecureDB;
GO

-- ============================================================
-- SECTION 1: CREATE DATABASE ROLES
-- ============================================================

-- Drop existing roles if they exist (for clean setup)
IF EXISTS (SELECT * FROM sys.database_principals WHERE name = 'db_Admin' AND type = 'R')
    DROP ROLE db_Admin;
IF EXISTS (SELECT * FROM sys.database_principals WHERE name = 'db_Instructor' AND type = 'R')
    DROP ROLE db_Instructor;
IF EXISTS (SELECT * FROM sys.database_principals WHERE name = 'db_TA' AND type = 'R')
    DROP ROLE db_TA;
IF EXISTS (SELECT * FROM sys.database_principals WHERE name = 'db_Student' AND type = 'R')
    DROP ROLE db_Student;
IF EXISTS (SELECT * FROM sys.database_principals WHERE name = 'db_Guest' AND type = 'R')
    DROP ROLE db_Guest;
GO

-- Create 5 Roles per project requirements
CREATE ROLE db_Admin;
CREATE ROLE db_Instructor;
CREATE ROLE db_TA;
CREATE ROLE db_Student;
CREATE ROLE db_Guest;
GO

PRINT '✓ Created 5 database roles: Admin, Instructor, TA, Student, Guest';
GO

-- ============================================================
-- SECTION 2: ADMIN ROLE PERMISSIONS (Clearance Level 4 - Top Secret)
-- Full System Access
-- ============================================================

-- STUDENT Table: Full Access
GRANT SELECT, INSERT, UPDATE, DELETE ON STUDENT TO db_Admin;

-- INSTRUCTOR Table: Full Access
GRANT SELECT, INSERT, UPDATE, DELETE ON INSTRUCTOR TO db_Admin;

-- COURSE Table: Full Access
GRANT SELECT, INSERT, UPDATE, DELETE ON COURSE TO db_Admin;

-- GRADES Table: Full Access
GRANT SELECT, INSERT, UPDATE, DELETE ON GRADES TO db_Admin;

-- ATTENDANCE Table: Full Access
GRANT SELECT, INSERT, UPDATE, DELETE ON ATTENDANCE TO db_Admin;

-- USERS Table: Full Access (Manage Users)
GRANT SELECT, INSERT, UPDATE, DELETE ON USERS TO db_Admin;

-- ROLE_REQUESTS Table: Full Access (Admin Dashboard)
GRANT SELECT, INSERT, UPDATE, DELETE ON ROLE_REQUESTS TO db_Admin;

-- Supporting Tables
GRANT SELECT, INSERT, UPDATE, DELETE ON COURSE_ENROLLMENT TO db_Admin;
GRANT SELECT, INSERT, UPDATE, DELETE ON COURSE_ASSIGNMENT TO db_Admin;
GRANT SELECT, INSERT ON AUDIT_LOG TO db_Admin;
GRANT SELECT ON SECURITY_CLASSIFICATION TO db_Admin;

-- Execute all stored procedures
GRANT EXECUTE ON SCHEMA::dbo TO db_Admin;

-- View definitions
GRANT VIEW DEFINITION ON SCHEMA::dbo TO db_Admin;
GO

PRINT '✓ Admin role: FULL ACCESS to all tables';
GO

-- ============================================================
-- SECTION 3: INSTRUCTOR ROLE PERMISSIONS (Clearance Level 3 - Secret)
-- Grades & Attendance for assigned courses
-- ============================================================

-- STUDENT Table: SELECT only (assigned students)
GRANT SELECT ON STUDENT TO db_Instructor;
DENY INSERT ON STUDENT TO db_Instructor;
DENY UPDATE ON STUDENT TO db_Instructor;
DENY DELETE ON STUDENT TO db_Instructor;

-- INSTRUCTOR Table: SELECT all, UPDATE own only
GRANT SELECT ON INSTRUCTOR TO db_Instructor;
GRANT UPDATE ON INSTRUCTOR TO db_Instructor;
DENY INSERT ON INSTRUCTOR TO db_Instructor;
DENY DELETE ON INSTRUCTOR TO db_Instructor;

-- COURSE Table: SELECT all
GRANT SELECT ON COURSE TO db_Instructor;
DENY INSERT ON COURSE TO db_Instructor;
DENY UPDATE ON COURSE TO db_Instructor;
DENY DELETE ON COURSE TO db_Instructor;

-- GRADES Table: SELECT/INSERT/UPDATE for assigned courses
GRANT SELECT ON GRADES TO db_Instructor;
GRANT INSERT ON GRADES TO db_Instructor;
GRANT UPDATE ON GRADES TO db_Instructor;
DENY DELETE ON GRADES TO db_Instructor;

-- ATTENDANCE Table: SELECT only (viewing attendance)
GRANT SELECT ON ATTENDANCE TO db_Instructor;
DENY INSERT ON ATTENDANCE TO db_Instructor;
DENY UPDATE ON ATTENDANCE TO db_Instructor;
DENY DELETE ON ATTENDANCE TO db_Instructor;

-- USERS Table: DENY ALL
DENY SELECT ON USERS TO db_Instructor;
DENY INSERT ON USERS TO db_Instructor;
DENY UPDATE ON USERS TO db_Instructor;
DENY DELETE ON USERS TO db_Instructor;

-- ROLE_REQUESTS Table: Can submit own requests
GRANT SELECT ON ROLE_REQUESTS TO db_Instructor;
GRANT INSERT ON ROLE_REQUESTS TO db_Instructor;
DENY UPDATE ON ROLE_REQUESTS TO db_Instructor;
DENY DELETE ON ROLE_REQUESTS TO db_Instructor;

-- Supporting Tables
GRANT SELECT ON COURSE_ENROLLMENT TO db_Instructor;
GRANT SELECT ON COURSE_ASSIGNMENT TO db_Instructor;
GRANT SELECT ON SECURITY_CLASSIFICATION TO db_Instructor;
GO

PRINT '✓ Instructor role: Grades (RW), Attendance (R), Students (R)';
GO

-- ============================================================
-- SECTION 4: TA ROLE PERMISSIONS (Clearance Level 2 - Confidential)
-- Attendance management, limited student data, NO grades access
-- ============================================================

-- STUDENT Table: SELECT only (assigned students)
GRANT SELECT ON STUDENT TO db_TA;
DENY INSERT ON STUDENT TO db_TA;
DENY UPDATE ON STUDENT TO db_TA;
DENY DELETE ON STUDENT TO db_TA;

-- INSTRUCTOR Table: DENY ALL
DENY SELECT ON INSTRUCTOR TO db_TA;
DENY INSERT ON INSTRUCTOR TO db_TA;
DENY UPDATE ON INSTRUCTOR TO db_TA;
DENY DELETE ON INSTRUCTOR TO db_TA;

-- COURSE Table: SELECT all
GRANT SELECT ON COURSE TO db_TA;
DENY INSERT ON COURSE TO db_TA;
DENY UPDATE ON COURSE TO db_TA;
DENY DELETE ON COURSE TO db_TA;

-- GRADES Table: DENY ALL (TAs cannot access grades)
DENY SELECT ON GRADES TO db_TA;
DENY INSERT ON GRADES TO db_TA;
DENY UPDATE ON GRADES TO db_TA;
DENY DELETE ON GRADES TO db_TA;

-- ATTENDANCE Table: SELECT/INSERT/UPDATE for assigned courses
GRANT SELECT ON ATTENDANCE TO db_TA;
GRANT INSERT ON ATTENDANCE TO db_TA;
GRANT UPDATE ON ATTENDANCE TO db_TA;
DENY DELETE ON ATTENDANCE TO db_TA;

-- USERS Table: DENY ALL
DENY SELECT ON USERS TO db_TA;
DENY INSERT ON USERS TO db_TA;
DENY UPDATE ON USERS TO db_TA;
DENY DELETE ON USERS TO db_TA;

-- ROLE_REQUESTS Table: Can submit own requests
GRANT SELECT ON ROLE_REQUESTS TO db_TA;
GRANT INSERT ON ROLE_REQUESTS TO db_TA;
DENY UPDATE ON ROLE_REQUESTS TO db_TA;
DENY DELETE ON ROLE_REQUESTS TO db_TA;

-- Supporting Tables
GRANT SELECT ON COURSE_ENROLLMENT TO db_TA;
GRANT SELECT ON COURSE_ASSIGNMENT TO db_TA;
GRANT SELECT ON SECURITY_CLASSIFICATION TO db_TA;
GO

PRINT '✓ TA role: Attendance (RW), Students (R), Grades (DENIED)';
GO

-- ============================================================
-- SECTION 5: STUDENT ROLE PERMISSIONS (Clearance Level 1 - Unclassified)
-- Own data access only
-- ============================================================

-- STUDENT Table: SELECT own only (enforced via views)
GRANT SELECT ON STUDENT TO db_Student;
DENY INSERT ON STUDENT TO db_Student;
DENY UPDATE ON STUDENT TO db_Student;
DENY DELETE ON STUDENT TO db_Student;

-- INSTRUCTOR Table: DENY ALL
DENY SELECT ON INSTRUCTOR TO db_Student;
DENY INSERT ON INSTRUCTOR TO db_Student;
DENY UPDATE ON INSTRUCTOR TO db_Student;
DENY DELETE ON INSTRUCTOR TO db_Student;

-- COURSE Table: SELECT all (public course info)
GRANT SELECT ON COURSE TO db_Student;
DENY INSERT ON COURSE TO db_Student;
DENY UPDATE ON COURSE TO db_Student;
DENY DELETE ON COURSE TO db_Student;

-- GRADES Table: SELECT own published only (enforced via views)
GRANT SELECT ON GRADES TO db_Student;
DENY INSERT ON GRADES TO db_Student;
DENY UPDATE ON GRADES TO db_Student;
DENY DELETE ON GRADES TO db_Student;

-- ATTENDANCE Table: SELECT own only (enforced via views)
GRANT SELECT ON ATTENDANCE TO db_Student;
DENY INSERT ON ATTENDANCE TO db_Student;
DENY UPDATE ON ATTENDANCE TO db_Student;
DENY DELETE ON ATTENDANCE TO db_Student;

-- USERS Table: DENY ALL
DENY SELECT ON USERS TO db_Student;
DENY INSERT ON USERS TO db_Student;
DENY UPDATE ON USERS TO db_Student;
DENY DELETE ON USERS TO db_Student;

-- ROLE_REQUESTS Table: Can submit own requests (Part B)
GRANT SELECT ON ROLE_REQUESTS TO db_Student;
GRANT INSERT ON ROLE_REQUESTS TO db_Student;
DENY UPDATE ON ROLE_REQUESTS TO db_Student;
DENY DELETE ON ROLE_REQUESTS TO db_Student;

-- Supporting Tables
GRANT SELECT ON COURSE_ENROLLMENT TO db_Student;
GRANT SELECT ON SECURITY_CLASSIFICATION TO db_Student;
GO

PRINT '✓ Student role: Own profile (R), Own grades (R), Own attendance (R)';
GO

-- ============================================================
-- SECTION 6: GUEST ROLE PERMISSIONS (Clearance Level 0 - Public)
-- Public course information ONLY
-- ============================================================

-- STUDENT Table: DENY ALL
DENY SELECT ON STUDENT TO db_Guest;
DENY INSERT ON STUDENT TO db_Guest;
DENY UPDATE ON STUDENT TO db_Guest;
DENY DELETE ON STUDENT TO db_Guest;

-- INSTRUCTOR Table: DENY ALL
DENY SELECT ON INSTRUCTOR TO db_Guest;
DENY INSERT ON INSTRUCTOR TO db_Guest;
DENY UPDATE ON INSTRUCTOR TO db_Guest;
DENY DELETE ON INSTRUCTOR TO db_Guest;

-- COURSE Table: Only PublicInfo column (enforced via view)
DENY SELECT ON COURSE TO db_Guest;    -- Will grant via view only
DENY INSERT ON COURSE TO db_Guest;
DENY UPDATE ON COURSE TO db_Guest;
DENY DELETE ON COURSE TO db_Guest;

-- GRADES Table: DENY ALL
DENY SELECT ON GRADES TO db_Guest;
DENY INSERT ON GRADES TO db_Guest;
DENY UPDATE ON GRADES TO db_Guest;
DENY DELETE ON GRADES TO db_Guest;

-- ATTENDANCE Table: DENY ALL
DENY SELECT ON ATTENDANCE TO db_Guest;
DENY INSERT ON ATTENDANCE TO db_Guest;
DENY UPDATE ON ATTENDANCE TO db_Guest;
DENY DELETE ON ATTENDANCE TO db_Guest;

-- USERS Table: DENY ALL
DENY SELECT ON USERS TO db_Guest;
DENY INSERT ON USERS TO db_Guest;
DENY UPDATE ON USERS TO db_Guest;
DENY DELETE ON USERS TO db_Guest;

-- ROLE_REQUESTS Table: DENY ALL
DENY SELECT ON ROLE_REQUESTS TO db_Guest;
DENY INSERT ON ROLE_REQUESTS TO db_Guest;
DENY UPDATE ON ROLE_REQUESTS TO db_Guest;
DENY DELETE ON ROLE_REQUESTS TO db_Guest;

-- All other tables: DENY
DENY SELECT ON COURSE_ENROLLMENT TO db_Guest;
DENY SELECT ON COURSE_ASSIGNMENT TO db_Guest;
DENY SELECT ON AUDIT_LOG TO db_Guest;
GO

PRINT '✓ Guest role: Public course info ONLY (via view)';
GO

-- ============================================================
-- SECTION 7: PERMISSION SUMMARY
-- ============================================================

PRINT '';
PRINT '═══════════════════════════════════════════════════════════════════';
PRINT '  RBAC PERMISSION MATRIX - SUMMARY';
PRINT '═══════════════════════════════════════════════════════════════════';
PRINT '';
PRINT '  ┌─────────────┬───────┬────────────┬──────┬─────────┬───────┐';
PRINT '  │ Table       │ Admin │ Instructor │ TA   │ Student │ Guest │';
PRINT '  ├─────────────┼───────┼────────────┼──────┼─────────┼───────┤';
PRINT '  │ STUDENT     │ CRUD  │ R          │ R    │ R (own) │ DENY  │';
PRINT '  │ INSTRUCTOR  │ CRUD  │ R/U (own)  │ DENY │ DENY    │ DENY  │';
PRINT '  │ COURSE      │ CRUD  │ R          │ R    │ R       │ View* │';
PRINT '  │ GRADES      │ CRUD  │ CRU        │ DENY │ R (own) │ DENY  │';
PRINT '  │ ATTENDANCE  │ CRUD  │ R          │ CRU  │ R (own) │ DENY  │';
PRINT '  │ USERS       │ CRUD  │ DENY       │ DENY │ DENY    │ DENY  │';
PRINT '  └─────────────┴───────┴────────────┴──────┴─────────┴───────┘';
PRINT '';
PRINT '  * Guest can only view PublicInfo via vw_PublicCourseInfo view';
PRINT '';
PRINT '  Legend: C=Create, R=Read, U=Update, D=Delete';
PRINT '═══════════════════════════════════════════════════════════════════';
GO
