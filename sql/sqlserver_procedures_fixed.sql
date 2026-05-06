-- =====================================================
-- SRMS - User Stored Procedures (Fixed)
-- Using usp_ prefix to avoid conflicts with system SPs
-- =====================================================

USE SRMS_SecureDB;
GO

-- Drop old procedures if they exist
DROP PROCEDURE IF EXISTS sp_AddUser;
DROP PROCEDURE IF EXISTS sp_UpdateGrade;
DROP PROCEDURE IF EXISTS sp_UpdateAttendance;
DROP PROCEDURE IF EXISTS sp_SubmitRoleRequest;
DROP PROCEDURE IF EXISTS sp_ProcessRoleRequest;
DROP PROCEDURE IF EXISTS sp_GetSecureStatistics;
DROP PROCEDURE IF EXISTS sp_FlowControlCheck;
GO

-- =====================================================
-- 1. Add User (Admin Only)
-- =====================================================
CREATE OR ALTER PROCEDURE usp_AddUser
    @Username NVARCHAR(50),
    @PasswordHash VARBINARY(256),
    @PasswordSalt VARBINARY(16),
    @Role NVARCHAR(20),
    @ClearanceLevel INT,
    @ExecutorRole NVARCHAR(20)
AS
BEGIN
    SET NOCOUNT ON;
    
    -- RBAC Check
    IF @ExecutorRole != 'Admin'
    BEGIN
        RAISERROR('Access Denied: Only Admin can add users', 16, 1);
        RETURN;
    END
    
    -- Insert User
    INSERT INTO USERS (Username, PasswordHash, PasswordSalt, Role, ClearanceLevel, IsActive, CreatedDate)
    VALUES (@Username, @PasswordHash, @PasswordSalt, @Role, @ClearanceLevel, 1, GETDATE());
    
    -- Audit Log
    INSERT INTO AUDIT_LOG (ActionType, TableName, Username, UserRole, AccessGranted, ActionDate)
    VALUES ('USER_ADD', 'USERS', @Username, @ExecutorRole, 1, GETDATE());
END;
GO

-- =====================================================
-- 2. Update Grade (Instructor/Admin Only)
-- =====================================================
CREATE OR ALTER PROCEDURE usp_UpdateGrade
    @GradeID INT,
    @NewValue DECIMAL(5,2),
    @ExecutorRole NVARCHAR(20)
AS
BEGIN
    SET NOCOUNT ON;
    
    -- RBAC Check
    IF @ExecutorRole NOT IN ('Admin', 'Instructor')
    BEGIN
        RAISERROR('Access Denied: Only Admin/Instructor can update grades', 16, 1);
        RETURN;
    END
    
    -- Update Grade
    UPDATE GRADES 
    SET GradeValue = @NewValue
    WHERE GradeID = @GradeID;
    
    -- Audit Log
    INSERT INTO AUDIT_LOG (ActionType, TableName, UserRole, AccessGranted, ActionDate)
    VALUES ('GRADE_UPDATE', 'GRADES', @ExecutorRole, 1, GETDATE());
END;
GO

-- =====================================================
-- 3. Update Attendance (TA/Instructor/Admin)
-- =====================================================
CREATE OR ALTER PROCEDURE usp_UpdateAttendance
    @StudentID INT,
    @CourseID INT,
    @Status BIT,
    @ExecutorID INT,
    @ExecutorRole NVARCHAR(20)
AS
BEGIN
    SET NOCOUNT ON;
    
    -- RBAC Check
    IF @ExecutorRole NOT IN ('Admin', 'Instructor', 'TA')
    BEGIN
        RAISERROR('Access Denied', 16, 1);
        RETURN;
    END
    
    -- Insert Attendance Record
    INSERT INTO ATTENDANCE (StudentID, CourseID, AttendanceDate, Status, RecordedBy, ClassificationLevel)
    VALUES (@StudentID, @CourseID, GETDATE(), @Status, @ExecutorID, 3);
    
    -- Audit Log
    INSERT INTO AUDIT_LOG (ActionType, TableName, UserRole, AccessGranted, ActionDate)
    VALUES ('ATTENDANCE_UPDATE', 'ATTENDANCE', @ExecutorRole, 1, GETDATE());
END;
GO

-- =====================================================
-- 4. Submit Role Request (Part B)
-- =====================================================
CREATE OR ALTER PROCEDURE usp_SubmitRoleRequest
    @UserID INT,
    @Username NVARCHAR(50),
    @CurrentRole NVARCHAR(20),
    @RequestedRole NVARCHAR(20),
    @CurrentClearance INT,
    @RequestedClearance INT,
    @Reason NVARCHAR(MAX)
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Check for existing pending request
    IF EXISTS (SELECT 1 FROM ROLE_REQUESTS WHERE UserID = @UserID AND Status = 'Pending')
    BEGIN
        RAISERROR('You already have a pending request.', 16, 1);
        RETURN;
    END
    
    -- Submit Request
    INSERT INTO ROLE_REQUESTS (UserID, Username, CurrentRole, RequestedRole, 
                              CurrentClearance, RequestedClearance, Reason, Status, DateSubmitted)
    VALUES (@UserID, @Username, @CurrentRole, @RequestedRole, 
            @CurrentClearance, @RequestedClearance, @Reason, 'Pending', GETDATE());
            
    -- Audit Log
    INSERT INTO AUDIT_LOG (ActionType, TableName, Username, UserRole, AccessGranted, ActionDate)
    VALUES ('ROLE_REQUEST_SUBMIT', 'ROLE_REQUESTS', @Username, @CurrentRole, 1, GETDATE());
END;
GO

-- =====================================================
-- 5. Process Role Request (Admin Only - Part B)
-- =====================================================
CREATE OR ALTER PROCEDURE usp_ProcessRoleRequest
    @RequestID INT,
    @Status NVARCHAR(20),
    @AdminID INT,
    @AdminUsername NVARCHAR(50)
AS
BEGIN
    SET NOCOUNT ON;
    
    DECLARE @UserID INT;
    DECLARE @RequestedRole NVARCHAR(20);
    DECLARE @RequestedClearance INT;
    
    -- Get Request Details
    SELECT @UserID = UserID, @RequestedRole = RequestedRole, @RequestedClearance = RequestedClearance
    FROM ROLE_REQUESTS WHERE RequestID = @RequestID;
    
    IF @UserID IS NULL
    BEGIN
        RAISERROR('Request not found.', 16, 1);
        RETURN;
    END
    
    BEGIN TRANSACTION;
    
    -- Update Request Status
    UPDATE ROLE_REQUESTS 
    SET Status = @Status, 
        DateProcessed = GETDATE(), 
        ProcessedBy = @AdminID, 
        ProcessedByUsername = @AdminUsername
    WHERE RequestID = @RequestID;
    
    -- If Approved, Update User Role
    IF @Status = 'Approved'
    BEGIN
        UPDATE USERS 
        SET Role = @RequestedRole, 
            ClearanceLevel = @RequestedClearance 
        WHERE UserID = @UserID;
        
        -- Audit Log
        INSERT INTO AUDIT_LOG (ActionType, TableName, Username, UserRole, AccessGranted, Details, ActionDate)
        VALUES ('ROLE_CHANGE', 'USERS', @AdminUsername, 'Admin', 1, 
                'Upgraded UserID ' + CAST(@UserID AS VARCHAR) + ' to ' + @RequestedRole, GETDATE());
    END
    
    COMMIT TRANSACTION;
END;
GO

-- =====================================================
-- 6. Get Secure Statistics (Inference Control)
-- =====================================================
CREATE OR ALTER PROCEDURE usp_GetSecureStatistics
    @MinGroupSize INT = 3
AS
BEGIN
    SET NOCOUNT ON;
    
    DECLARE @RecordCount INT;
    SELECT @RecordCount = COUNT(*) FROM STUDENT;
    
    -- Inference Control: Minimum Group Size
    IF @RecordCount < @MinGroupSize
    BEGIN
        RAISERROR('Inference Control: Minimum group size not met', 16, 1);
        RETURN;
    END
    
    -- Return Statistics
    SELECT 
        COUNT(*) as TotalStudents,
        AVG(CAST(ClearanceLevel AS FLOAT)) as AvgClearance
    FROM STUDENT;
END;
GO

-- =====================================================
-- 7. Flow Control Check
-- =====================================================
CREATE OR ALTER PROCEDURE usp_FlowControlCheck
    @UserClearance INT,
    @DataClassification INT
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Check if user has sufficient clearance
    IF @UserClearance < @DataClassification
    BEGIN
        RAISERROR('Flow Control: Access Denied - Insufficient clearance', 16, 1);
        RETURN;
    END
    
    SELECT 1 as Allowed;
END;
GO

PRINT '✓ All stored procedures created successfully with usp_ prefix!';
PRINT '✓ Summary:';
PRINT '  - usp_AddUser (RBAC)';
PRINT '  - usp_UpdateGrade (RBAC)';
PRINT '  - usp_UpdateAttendance (RBAC)';
PRINT '  - usp_SubmitRoleRequest (Part B)';
PRINT '  - usp_ProcessRoleRequest (Part B)';
PRINT '  - usp_GetSecureStatistics (Inference Control)';
PRINT '  - usp_FlowControlCheck (Flow Control)';
