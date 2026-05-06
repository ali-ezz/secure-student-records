-- ============================================================
-- SRMS - SAMPLE DATA
-- Database Security Term Project Phase 2
-- Run this script LAST after all other scripts
-- ============================================================

USE SRMS_SecureDB;
GO

-- ============================================================
-- SECTION 1: SAMPLE INSTRUCTORS
-- ============================================================

-- Open encryption key
OPEN SYMMETRIC KEY SRMS_SymmetricKey DECRYPTION BY CERTIFICATE SRMS_Certificate;

INSERT INTO INSTRUCTOR (FullName, Email, Phone, Phone_Display, Department, Title, ClearanceLevel, ClassificationLevel)
VALUES 
('Dr. John Smith', 'john.smith@university.edu', EncryptByKey(Key_GUID('SRMS_SymmetricKey'), '555-0101'), '555-****', 'Computer Science', 'Professor', 3, 2),
('Dr. Sarah Johnson', 'sarah.johnson@university.edu', EncryptByKey(Key_GUID('SRMS_SymmetricKey'), '555-0102'), '555-****', 'Computer Science', 'Associate Professor', 3, 2),
('Dr. Michael Brown', 'michael.brown@university.edu', EncryptByKey(Key_GUID('SRMS_SymmetricKey'), '555-0103'), '555-****', 'Information Systems', 'Professor', 3, 2),
('Dr. Emily Davis', 'emily.davis@university.edu', EncryptByKey(Key_GUID('SRMS_SymmetricKey'), '555-0104'), '555-****', 'Data Science', 'Assistant Professor', 3, 2);

PRINT '✓ Inserted 4 instructors';
GO

-- ============================================================
-- SECTION 2: SAMPLE STUDENTS
-- ============================================================

OPEN SYMMETRIC KEY SRMS_SymmetricKey DECRYPTION BY CERTIFICATE SRMS_Certificate;

INSERT INTO STUDENT (StudentID_Encrypted, FullName, Email, Phone, Phone_Display, DOB, Department, Status, ClearanceLevel, ClassificationLevel)
VALUES 
(EncryptByKey(Key_GUID('SRMS_SymmetricKey'), '1001'), 'Alice Anderson', 'alice.anderson@student.edu', EncryptByKey(Key_GUID('SRMS_SymmetricKey'), '555-1001'), '555-****', '2000-05-15', 'Computer Science', 'Active', 1, 2),
(EncryptByKey(Key_GUID('SRMS_SymmetricKey'), '1002'), 'Bob Williams', 'bob.williams@student.edu', EncryptByKey(Key_GUID('SRMS_SymmetricKey'), '555-1002'), '555-****', '2001-03-22', 'Computer Science', 'Active', 1, 2),
(EncryptByKey(Key_GUID('SRMS_SymmetricKey'), '1003'), 'Carol Martinez', 'carol.martinez@student.edu', EncryptByKey(Key_GUID('SRMS_SymmetricKey'), '555-1003'), '555-****', '2000-11-08', 'Information Systems', 'Active', 1, 2),
(EncryptByKey(Key_GUID('SRMS_SymmetricKey'), '1004'), 'David Lee', 'david.lee@student.edu', EncryptByKey(Key_GUID('SRMS_SymmetricKey'), '555-1004'), '555-****', '2001-07-30', 'Data Science', 'Active', 1, 2),
(EncryptByKey(Key_GUID('SRMS_SymmetricKey'), '1005'), 'Eva Chen', 'eva.chen@student.edu', EncryptByKey(Key_GUID('SRMS_SymmetricKey'), '555-1005'), '555-****', '2000-09-12', 'Computer Science', 'Active', 1, 2),
(EncryptByKey(Key_GUID('SRMS_SymmetricKey'), '1006'), 'Frank Wilson', 'frank.wilson@student.edu', EncryptByKey(Key_GUID('SRMS_SymmetricKey'), '555-1006'), '555-****', '2001-01-25', 'Computer Science', 'Active', 1, 2),
(EncryptByKey(Key_GUID('SRMS_SymmetricKey'), '1007'), 'Grace Taylor', 'grace.taylor@student.edu', EncryptByKey(Key_GUID('SRMS_SymmetricKey'), '555-1007'), '555-****', '2000-04-18', 'Information Systems', 'Active', 1, 2),
(EncryptByKey(Key_GUID('SRMS_SymmetricKey'), '1008'), 'Henry Thomas', 'henry.thomas@student.edu', EncryptByKey(Key_GUID('SRMS_SymmetricKey'), '555-1008'), '555-****', '2001-12-05', 'Data Science', 'Active', 1, 2);

CLOSE SYMMETRIC KEY SRMS_SymmetricKey;

PRINT '✓ Inserted 8 students';
GO

-- ============================================================
-- SECTION 3: SAMPLE COURSES
-- ============================================================

INSERT INTO COURSE (CourseCode, CourseName, Description, PublicInfo, Credits, Department, Semester, Year, MaxCapacity, InstructorID, ClassificationLevel)
VALUES 
('CS101', 'Introduction to Programming', 'Basic programming concepts using Python', 'Learn programming fundamentals. Open to all majors.', 3, 'Computer Science', 'Fall', 2024, 40, 1, 1),
('CS201', 'Database Systems', 'Introduction to database design and SQL', 'Essential database concepts for data management.', 3, 'Computer Science', 'Fall', 2024, 35, 1, 1),
('CS301', 'Database Security', 'Advanced database security concepts', 'Learn to protect sensitive data in databases.', 3, 'Computer Science', 'Fall', 2024, 30, 2, 1),
('IS201', 'Information Systems Management', 'Managing organizational information systems', 'Business-focused IT management course.', 3, 'Information Systems', 'Fall', 2024, 35, 3, 1),
('DS101', 'Data Science Fundamentals', 'Introduction to data science and analytics', 'Explore data-driven decision making.', 3, 'Data Science', 'Fall', 2024, 40, 4, 1);

PRINT '✓ Inserted 5 courses';
GO

-- ============================================================
-- SECTION 4: SAMPLE USERS (Authentication)
-- ============================================================

DECLARE @Salt VARBINARY(128);

-- Admin user
SET @Salt = CAST(NEWID() AS VARBINARY(128));
INSERT INTO USERS (Username, PasswordHash, PasswordSalt, Role, ClearanceLevel)
VALUES ('admin', HASHBYTES('SHA2_256', 'admin123' + CAST(@Salt AS NVARCHAR(256))), @Salt, 'Admin', 4);

-- Instructor users (linked to INSTRUCTOR table)
SET @Salt = CAST(NEWID() AS VARBINARY(128));
INSERT INTO USERS (Username, PasswordHash, PasswordSalt, Role, ClearanceLevel, LinkedID, LinkedType)
VALUES ('prof_smith', HASHBYTES('SHA2_256', 'prof123' + CAST(@Salt AS NVARCHAR(256))), @Salt, 'Instructor', 3, 1, 'Instructor');

SET @Salt = CAST(NEWID() AS VARBINARY(128));
INSERT INTO USERS (Username, PasswordHash, PasswordSalt, Role, ClearanceLevel, LinkedID, LinkedType)
VALUES ('prof_johnson', HASHBYTES('SHA2_256', 'prof123' + CAST(@Salt AS NVARCHAR(256))), @Salt, 'Instructor', 3, 2, 'Instructor');

-- TA user
SET @Salt = CAST(NEWID() AS VARBINARY(128));
INSERT INTO USERS (Username, PasswordHash, PasswordSalt, Role, ClearanceLevel, LinkedID, LinkedType)
VALUES ('ta_williams', HASHBYTES('SHA2_256', 'ta123' + CAST(@Salt AS NVARCHAR(256))), @Salt, 'TA', 2, NULL, 'TA');

-- Student users (linked to STUDENT table)
SET @Salt = CAST(NEWID() AS VARBINARY(128));
INSERT INTO USERS (Username, PasswordHash, PasswordSalt, Role, ClearanceLevel, LinkedID, LinkedType)
VALUES ('student1', HASHBYTES('SHA2_256', 'student123' + CAST(@Salt AS NVARCHAR(256))), @Salt, 'Student', 1, 1, 'Student');

SET @Salt = CAST(NEWID() AS VARBINARY(128));
INSERT INTO USERS (Username, PasswordHash, PasswordSalt, Role, ClearanceLevel, LinkedID, LinkedType)
VALUES ('student2', HASHBYTES('SHA2_256', 'student123' + CAST(@Salt AS NVARCHAR(256))), @Salt, 'Student', 1, 2, 'Student');

SET @Salt = CAST(NEWID() AS VARBINARY(128));
INSERT INTO USERS (Username, PasswordHash, PasswordSalt, Role, ClearanceLevel, LinkedID, LinkedType)
VALUES ('student3', HASHBYTES('SHA2_256', 'student123' + CAST(@Salt AS NVARCHAR(256))), @Salt, 'Student', 1, 3, 'Student');

-- Guest user
SET @Salt = CAST(NEWID() AS VARBINARY(128));
INSERT INTO USERS (Username, PasswordHash, PasswordSalt, Role, ClearanceLevel)
VALUES ('guest', HASHBYTES('SHA2_256', 'guest123' + CAST(@Salt AS NVARCHAR(256))), @Salt, 'Guest', 0);

PRINT '✓ Inserted 8 users (admin, 2 instructors, 1 TA, 3 students, 1 guest)';
GO

-- ============================================================
-- SECTION 5: COURSE ENROLLMENTS
-- ============================================================

INSERT INTO COURSE_ENROLLMENT (StudentID, CourseID, Semester, Year)
VALUES 
-- CS101 - 5 students
(1, 1, 'Fall', 2024), (2, 1, 'Fall', 2024), (3, 1, 'Fall', 2024), (4, 1, 'Fall', 2024), (5, 1, 'Fall', 2024),
-- CS201 - 4 students
(1, 2, 'Fall', 2024), (2, 2, 'Fall', 2024), (5, 2, 'Fall', 2024), (6, 2, 'Fall', 2024),
-- CS301 - 5 students
(1, 3, 'Fall', 2024), (2, 3, 'Fall', 2024), (5, 3, 'Fall', 2024), (6, 3, 'Fall', 2024), (7, 3, 'Fall', 2024),
-- IS201 - 3 students
(3, 4, 'Fall', 2024), (7, 4, 'Fall', 2024), (8, 4, 'Fall', 2024),
-- DS101 - 4 students
(4, 5, 'Fall', 2024), (5, 5, 'Fall', 2024), (6, 5, 'Fall', 2024), (8, 5, 'Fall', 2024);

PRINT '✓ Enrolled students in courses';
GO

-- ============================================================
-- SECTION 6: COURSE ASSIGNMENTS (Instructor & TA)
-- ============================================================

INSERT INTO COURSE_ASSIGNMENT (CourseID, UserID, AssignmentType, Semester, Year)
VALUES 
-- Prof Smith teaches CS101 and CS201
(1, 2, 'Instructor', 'Fall', 2024),
(2, 2, 'Instructor', 'Fall', 2024),
-- Prof Johnson teaches CS301
(3, 3, 'Instructor', 'Fall', 2024),
-- TA Williams assigned to CS101 and CS301
(1, 4, 'TA', 'Fall', 2024),
(3, 4, 'TA', 'Fall', 2024);

PRINT '✓ Assigned instructors and TAs to courses';
GO

-- ============================================================
-- SECTION 7: SAMPLE GRADES (Encrypted)
-- ============================================================

OPEN SYMMETRIC KEY SRMS_SymmetricKey DECRYPTION BY CERTIFICATE SRMS_Certificate;

-- CS101 Grades (5 students - enough for inference control)
INSERT INTO GRADES (StudentID, StudentID_Encrypted, CourseID, GradeValue, GradeValue_Display, GradeLetter, Semester, EnteredBy, IsPublished, IsFinal, ClassificationLevel)
VALUES 
(1, EncryptByKey(Key_GUID('SRMS_SymmetricKey'), '1'), 1, EncryptByKey(Key_GUID('SRMS_SymmetricKey'), '95.5'), 95.5, 'A', 'Fall', 1, 1, 1, 3),
(2, EncryptByKey(Key_GUID('SRMS_SymmetricKey'), '2'), 1, EncryptByKey(Key_GUID('SRMS_SymmetricKey'), '88.0'), 88.0, 'B+', 'Fall', 1, 1, 1, 3),
(3, EncryptByKey(Key_GUID('SRMS_SymmetricKey'), '3'), 1, EncryptByKey(Key_GUID('SRMS_SymmetricKey'), '92.0'), 92.0, 'A-', 'Fall', 1, 1, 1, 3),
(4, EncryptByKey(Key_GUID('SRMS_SymmetricKey'), '4'), 1, EncryptByKey(Key_GUID('SRMS_SymmetricKey'), '78.5'), 78.5, 'C+', 'Fall', 1, 1, 1, 3),
(5, EncryptByKey(Key_GUID('SRMS_SymmetricKey'), '5'), 1, EncryptByKey(Key_GUID('SRMS_SymmetricKey'), '85.0'), 85.0, 'B', 'Fall', 1, 1, 1, 3),

-- CS301 Grades (5 students)
(1, EncryptByKey(Key_GUID('SRMS_SymmetricKey'), '1'), 3, EncryptByKey(Key_GUID('SRMS_SymmetricKey'), '97.0'), 97.0, 'A+', 'Fall', 2, 1, 1, 3),
(2, EncryptByKey(Key_GUID('SRMS_SymmetricKey'), '2'), 3, EncryptByKey(Key_GUID('SRMS_SymmetricKey'), '89.5'), 89.5, 'B+', 'Fall', 2, 1, 1, 3),
(5, EncryptByKey(Key_GUID('SRMS_SymmetricKey'), '5'), 3, EncryptByKey(Key_GUID('SRMS_SymmetricKey'), '93.0'), 93.0, 'A-', 'Fall', 2, 1, 1, 3),
(6, EncryptByKey(Key_GUID('SRMS_SymmetricKey'), '6'), 3, EncryptByKey(Key_GUID('SRMS_SymmetricKey'), '91.0'), 91.0, 'A-', 'Fall', 2, 1, 1, 3),
(7, EncryptByKey(Key_GUID('SRMS_SymmetricKey'), '7'), 3, EncryptByKey(Key_GUID('SRMS_SymmetricKey'), '86.5'), 86.5, 'B', 'Fall', 2, 1, 1, 3);

CLOSE SYMMETRIC KEY SRMS_SymmetricKey;

PRINT '✓ Inserted 10 grades (encrypted)';
GO

-- ============================================================
-- SECTION 8: SAMPLE ATTENDANCE
-- ============================================================

INSERT INTO ATTENDANCE (StudentID, CourseID, AttendanceDate, Status, RecordedBy, ClassificationLevel)
VALUES 
-- CS101 attendance
(1, 1, '2024-09-01', 1, 4, 3),
(2, 1, '2024-09-01', 1, 4, 3),
(3, 1, '2024-09-01', 0, 4, 3),
(4, 1, '2024-09-01', 1, 4, 3),
(5, 1, '2024-09-01', 1, 4, 3),
(1, 1, '2024-09-08', 1, 4, 3),
(2, 1, '2024-09-08', 0, 4, 3),
(3, 1, '2024-09-08', 1, 4, 3),
(4, 1, '2024-09-08', 1, 4, 3),
(5, 1, '2024-09-08', 1, 4, 3),

-- CS301 attendance
(1, 3, '2024-09-02', 1, 4, 3),
(2, 3, '2024-09-02', 1, 4, 3),
(5, 3, '2024-09-02', 1, 4, 3),
(6, 3, '2024-09-02', 0, 4, 3),
(7, 3, '2024-09-02', 1, 4, 3);

PRINT '✓ Inserted 15 attendance records';
GO

-- ============================================================
-- SECTION 9: SAMPLE ROLE REQUEST (Part B Demo)
-- ============================================================

INSERT INTO ROLE_REQUESTS (UserID, Username, CurrentRole, RequestedRole, CurrentClearance, RequestedClearance, Reason, Status, DateSubmitted)
VALUES 
(5, 'student1', 'Student', 'TA', 1, 2, 'I have completed all coursework with excellent grades and would like to assist with teaching Database Security (CS301).', 'Pending', GETDATE());

PRINT '✓ Inserted 1 pending role request (Part B demo)';
GO

-- ============================================================
-- SECTION 10: SAMPLE AUDIT LOG ENTRIES
-- ============================================================

INSERT INTO AUDIT_LOG (ActionType, UserID, Username, UserRole, UserClearance, Description, AccessGranted, ActionDate)
VALUES 
('SYSTEM_INIT', 1, 'admin', 'Admin', 4, 'Database initialized with sample data', 1, GETDATE()),
('LOGIN_SUCCESS', 1, 'admin', 'Admin', 4, 'Admin logged in', 1, GETDATE()),
('DATA_SEED', 1, 'admin', 'Admin', 4, 'Sample data inserted', 1, GETDATE());

PRINT '✓ Inserted audit log entries';
GO

-- ============================================================
-- SECTION 11: SUMMARY
-- ============================================================

PRINT '';
PRINT '═══════════════════════════════════════════════════════════════════';
PRINT '  SAMPLE DATA - SUMMARY';
PRINT '═══════════════════════════════════════════════════════════════════';
PRINT '';
PRINT '  Data Inserted:';
PRINT '  ───────────────────────────────────────────────────────';
PRINT '  │ Table               │ Count │ Encryption          │';
PRINT '  ├─────────────────────┼───────┼─────────────────────┤';
PRINT '  │ INSTRUCTOR          │ 4     │ Phone encrypted     │';
PRINT '  │ STUDENT             │ 8     │ ID & Phone encrypted│';
PRINT '  │ COURSE              │ 5     │ No                  │';
PRINT '  │ USERS               │ 8     │ Password hashed     │';
PRINT '  │ COURSE_ENROLLMENT   │ 21    │ No                  │';
PRINT '  │ COURSE_ASSIGNMENT   │ 5     │ No                  │';
PRINT '  │ GRADES              │ 10    │ Grade value encrypted│';
PRINT '  │ ATTENDANCE          │ 15    │ No                  │';
PRINT '  │ ROLE_REQUESTS       │ 1     │ Pending (Part B)    │';
PRINT '  │ AUDIT_LOG           │ 3     │ No                  │';
PRINT '  ───────────────────────────────────────────────────────';
PRINT '';
PRINT '  Test Accounts:';
PRINT '  ───────────────────────────────────────────────────────';
PRINT '  │ Username      │ Password    │ Role       │ Level │';
PRINT '  ├───────────────┼─────────────┼────────────┼───────┤';
PRINT '  │ admin         │ admin123    │ Admin      │ 4     │';
PRINT '  │ prof_smith    │ prof123     │ Instructor │ 3     │';
PRINT '  │ prof_johnson  │ prof123     │ Instructor │ 3     │';
PRINT '  │ ta_williams   │ ta123       │ TA         │ 2     │';
PRINT '  │ student1      │ student123  │ Student    │ 1     │';
PRINT '  │ student2      │ student123  │ Student    │ 1     │';
PRINT '  │ student3      │ student123  │ Student    │ 1     │';
PRINT '  │ guest         │ guest123    │ Guest      │ 0     │';
PRINT '  ───────────────────────────────────────────────────────';
PRINT '';
PRINT '═══════════════════════════════════════════════════════════════════';
GO
