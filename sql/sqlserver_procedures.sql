-- ============================================================
-- SRMS - STORED PROCEDURES (All 5 Security Models + Part B)
-- Database Security Term Project Phase 2
-- Run this script FOURTH after sqlserver_views.sql
-- ============================================================

USE SRMS_SecureDB;
GO

-- ============================================================
-- SECTION 1: AUTHENTICATION PROCEDURES
-- ============================================================

-- User Login with account locking
CREATE OR ALTER PROCEDURE sp_UserLogin
    @Username NVARCHAR(50),
    @Password NVARCHAR(100),
    @Success BIT OUTPUT,
    @UserRole NVARCHAR(20) OUTPUT,
    @ClearanceLevel INT OUTPUT,
    @UserID INT OUTPUT,
    @ErrorMessage NVARCHAR(200) OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    
    DECLARE @StoredHash VARBINARY(256);
    DECLARE @StoredSalt VARBINARY(128);
    DECLARE @ComputedHash VARBINARY(256);
    DECLARE @IsActive BIT;
    DECLARE @IsLocked BIT;
    DECLARE @FailedAttempts INT;
    
    SET @Success = 0;
    SET @UserRole = NULL;
    SET @ClearanceLevel = 0;
    SET @UserID = 0;
    SET @ErrorMessage = '';
    
    -- Check if user exists
    SELECT 
        @UserID = UserID,
        @StoredHash = PasswordHash,
        @StoredSalt = PasswordSalt,
        @UserRole = Role,
        @ClearanceLevel = ClearanceLevel,
        @IsActive = IsActive,
        @IsLocked = IsLocked,
        @FailedAttempts = FailedLoginAttempts
    FROM USERS
    WHERE Username = @Username;
    
    IF @UserID IS NULL OR @UserID = 0
    BEGIN
        SET @ErrorMessage = 'Invalid username or password';
        SET @UserID = 0;
        
        INSERT INTO AUDIT_LOG (ActionType, Description, Username, ActionDate)
        VALUES ('LOGIN_FAILED', 'User not found: ' + @Username, @Username, GETDATE());
        RETURN;
    END
    
    -- Check if account is locked
    IF @IsLocked = 1
    BEGIN
        SET @ErrorMessage = 'Account is locked. Contact administrator.';
        SET @UserID = 0;
        RETURN;
    END
    
    -- Check if account is active
    IF @IsActive = 0
    BEGIN
        SET @ErrorMessage = 'Account is inactive.';
        SET @UserID = 0;
        RETURN;
    END
    
    -- Verify password (SHA2_256 hash)
    SET @ComputedHash = HASHBYTES('SHA2_256', @Password + CAST(@StoredSalt AS NVARCHAR(256)));
    
    IF @ComputedHash = @StoredHash
    BEGIN
        SET @Success = 1;
        
        -- Update last login, reset failed attempts
        UPDATE USERS
        SET LastLoginDate = GETDATE(),
            FailedLoginAttempts = 0
        WHERE UserID = @UserID;
        
        -- Log successful login
        INSERT INTO AUDIT_LOG (ActionType, UserID, Username, UserRole, UserClearance, 
                              AccessGranted, Description, ActionDate)
        VALUES ('LOGIN_SUCCESS', @UserID, @Username, @UserRole, @ClearanceLevel, 
                1, 'Successful login', GETDATE());
    END
    ELSE
    BEGIN
        SET @FailedAttempts = @FailedAttempts + 1;
        
        -- Lock account after 5 failed attempts
        IF @FailedAttempts >= 5
        BEGIN
            UPDATE USERS
            SET IsLocked = 1, FailedLoginAttempts = @FailedAttempts
            WHERE UserID = @UserID;
            SET @ErrorMessage = 'Account locked due to too many failed attempts.';
        END
        ELSE
        BEGIN
            UPDATE USERS SET FailedLoginAttempts = @FailedAttempts WHERE UserID = @UserID;
            SET @ErrorMessage = 'Invalid password. Attempts: ' + CAST(@FailedAttempts AS NVARCHAR(10)) + '/5';
        END
        
        SET @UserID = 0;
        
        INSERT INTO AUDIT_LOG (ActionType, UserID, Username, UserRole, AccessGranted, Description)
        VALUES ('LOGIN_FAILED', @UserID, @Username, @UserRole, 0, 
                'Failed login attempt ' + CAST(@FailedAttempts AS NVARCHAR(10)));
    END
END;
GO

PRINT '✓ Created sp_UserLogin (Authentication)';
GO

-- ============================================================
-- SECTION 2: MLS PROCEDURES (Bell-LaPadula)
-- ============================================================

-- No Read Up (NRU) Check - MANDATORY
CREATE OR ALTER PROCEDURE sp_MLSReadCheck
    @UserClearance INT,
    @DataClassification INT,
    @CanRead BIT OUTPUT,
    @Message NVARCHAR(200) OUTPUT
AS
BEGIN
    -- NO READ UP: User clearance must be >= Data classification
    IF @UserClearance >= @DataClassification
    BEGIN
        SET @CanRead = 1;
        SET @Message = 'READ ALLOWED: Clearance ' + CAST(@UserClearance AS NVARCHAR(10)) +
                       ' >= Classification ' + CAST(@DataClassification AS NVARCHAR(10));
    END
    ELSE
    BEGIN
        SET @CanRead = 0;
        SET @Message = 'READ BLOCKED (No Read Up): Clearance ' + CAST(@UserClearance AS NVARCHAR(10)) +
                       ' < Classification ' + CAST(@DataClassification AS NVARCHAR(10));
    END
END;
GO

PRINT '✓ Created sp_MLSReadCheck (No Read Up)';
GO

-- No Write Down (NWD) Check - BONUS
CREATE OR ALTER PROCEDURE sp_MLSWriteCheck
    @UserClearance INT,
    @DataClassification INT,
    @CanWrite BIT OUTPUT,
    @Message NVARCHAR(200) OUTPUT
AS
BEGIN
    -- NO WRITE DOWN: User clearance must be <= Data classification
    IF @UserClearance <= @DataClassification
    BEGIN
        SET @CanWrite = 1;
        SET @Message = 'WRITE ALLOWED: Clearance ' + CAST(@UserClearance AS NVARCHAR(10)) +
                       ' <= Classification ' + CAST(@DataClassification AS NVARCHAR(10));
    END
    ELSE
    BEGIN
        SET @CanWrite = 0;
        SET @Message = 'WRITE BLOCKED (No Write Down): Clearance ' + CAST(@UserClearance AS NVARCHAR(10)) +
                       ' > Classification ' + CAST(@DataClassification AS NVARCHAR(10));
    END
END;
GO

PRINT '✓ Created sp_MLSWriteCheck (No Write Down - BONUS)';
GO

-- Combined MLS Check
CREATE OR ALTER PROCEDURE sp_MLSAccessCheck
    @UserID INT,
    @TableName NVARCHAR(50),
    @Operation NVARCHAR(10),  -- 'READ' or 'WRITE'
    @AccessGranted BIT OUTPUT,
    @Message NVARCHAR(200) OUTPUT
AS
BEGIN
    DECLARE @UserClearance INT;
    DECLARE @DataClassification INT;
    
    -- Get user clearance
    SELECT @UserClearance = ClearanceLevel FROM USERS WHERE UserID = @UserID;
    
    -- Get data classification based on table
    SET @DataClassification = 
        CASE @TableName
            WHEN 'GRADES' THEN 3        -- Secret
            WHEN 'ATTENDANCE' THEN 3    -- Secret
            WHEN 'STUDENT' THEN 2       -- Confidential
            WHEN 'INSTRUCTOR' THEN 2    -- Confidential
            WHEN 'COURSE' THEN 1        -- Unclassified
            ELSE 0                      -- Public
        END;
    
    IF @Operation = 'READ'
    BEGIN
        EXEC sp_MLSReadCheck @UserClearance, @DataClassification, @AccessGranted OUTPUT, @Message OUTPUT;
    END
    ELSE IF @Operation = 'WRITE'
    BEGIN
        EXEC sp_MLSWriteCheck @UserClearance, @DataClassification, @AccessGranted OUTPUT, @Message OUTPUT;
    END
    
    -- Log the access check
    INSERT INTO AUDIT_LOG (ActionType, UserID, TableName, UserClearance, DataClassification, AccessGranted, Description)
    VALUES ('MLS_CHECK', @UserID, @TableName, @UserClearance, @DataClassification, @AccessGranted, @Message);
END;
GO

PRINT '✓ Created sp_MLSAccessCheck (Combined MLS)';
GO

-- ============================================================
-- SECTION 3: INFERENCE CONTROL PROCEDURES
-- ============================================================

-- Get Course Statistics (with Inference Control - min 3 records)
CREATE OR ALTER PROCEDURE sp_GetCourseStatistics
    @CourseID INT,
    @UserID INT
AS
BEGIN
    DECLARE @StudentCount INT;
    DECLARE @UserRole NVARCHAR(20);
    
    SELECT @UserRole = Role FROM USERS WHERE UserID = @UserID;
    
    -- Count students in course
    SELECT @StudentCount = COUNT(DISTINCT StudentID) 
    FROM GRADES 
    WHERE CourseID = @CourseID AND IsFinal = 1;
    
    -- INFERENCE CONTROL: Minimum group size of 3
    IF @StudentCount < 3
    BEGIN
        SELECT 
            'Statistics unavailable' AS Message,
            'Insufficient data for statistical analysis (minimum 3 students required)' AS Reason,
            @StudentCount AS ActualCount,
            3 AS RequiredMinimum;
            
        INSERT INTO AUDIT_LOG (ActionType, UserID, TableName, Description, AccessGranted)
        VALUES ('INFERENCE_BLOCKED', @UserID, 'GRADES', 
                'Statistics blocked - only ' + CAST(@StudentCount AS NVARCHAR(10)) + ' students', 0);
        RETURN;
    END
    
    -- Return aggregate statistics only (no individual data)
    SELECT 
        c.CourseName,
        c.CourseCode,
        COUNT(g.GradeID) AS TotalGrades,
        ROUND(AVG(g.GradeValue_Display), 2) AS AverageGrade,
        MIN(g.GradeValue_Display) AS MinGrade,
        MAX(g.GradeValue_Display) AS MaxGrade,
        ROUND(STDEV(g.GradeValue_Display), 2) AS StandardDeviation
    FROM GRADES g
    INNER JOIN COURSE c ON g.CourseID = c.CourseID
    WHERE g.CourseID = @CourseID AND g.IsFinal = 1
    GROUP BY c.CourseName, c.CourseCode
    HAVING COUNT(g.GradeID) >= 3;  -- Enforce minimum
    
    INSERT INTO AUDIT_LOG (ActionType, UserID, TableName, Description, AccessGranted)
    VALUES ('INFERENCE_ALLOWED', @UserID, 'GRADES', 'Course statistics retrieved', 1);
END;
GO

PRINT '✓ Created sp_GetCourseStatistics (Inference Control)';
GO

-- ============================================================
-- SECTION 4: FLOW CONTROL PROCEDURES
-- ============================================================

-- Check Data Flow (Downflow Prevention)
CREATE OR ALTER PROCEDURE sp_CheckDataFlow
    @SourceClassification INT,
    @DestinationClassification INT,
    @AllowFlow BIT OUTPUT,
    @Message NVARCHAR(200) OUTPUT
AS
BEGIN
    -- FLOW CONTROL: Cannot flow from higher to lower classification
    IF @SourceClassification > @DestinationClassification
    BEGIN
        SET @AllowFlow = 0;
        SET @Message = 'FLOW BLOCKED: Cannot transfer data from level ' + 
                       CAST(@SourceClassification AS NVARCHAR(10)) + ' to level ' +
                       CAST(@DestinationClassification AS NVARCHAR(10)) + ' (Downflow prevented)';
                       
        INSERT INTO AUDIT_LOG (ActionType, DataClassification, Description, AccessGranted)
        VALUES ('FLOW_BLOCKED', @SourceClassification, @Message, 0);
    END
    ELSE
    BEGIN
        SET @AllowFlow = 1;
        SET @Message = 'Flow allowed';
    END
END;
GO

PRINT '✓ Created sp_CheckDataFlow (Flow Control)';
GO

-- Export Data Check (BONUS - Block export of classified data)
CREATE OR ALTER PROCEDURE sp_CheckExportAllowed
    @TableName NVARCHAR(100),
    @UserID INT,
    @ExportAllowed BIT OUTPUT,
    @Message NVARCHAR(200) OUTPUT
AS
BEGIN
    DECLARE @DataClassification INT;
    DECLARE @UserClearance INT;
    
    -- Get data classification
    SET @DataClassification = 
        CASE @TableName
            WHEN 'GRADES' THEN 3        -- Secret
            WHEN 'ATTENDANCE' THEN 3    -- Secret
            WHEN 'STUDENT' THEN 2       -- Confidential
            WHEN 'INSTRUCTOR' THEN 2    -- Confidential
            WHEN 'COURSE' THEN 1        -- Unclassified
            ELSE 0
        END;
    
    SELECT @UserClearance = ClearanceLevel FROM USERS WHERE UserID = @UserID;
    
    -- BONUS: Block export of Secret/Top Secret data
    IF @DataClassification >= 3
    BEGIN
        SET @ExportAllowed = 0;
        SET @Message = 'EXPORT BLOCKED: Cannot export Secret or Top Secret data.';
        
        INSERT INTO AUDIT_LOG (ActionType, UserID, TableName, DataClassification, AccessGranted, Description)
        VALUES ('EXPORT_BLOCKED', @UserID, @TableName, @DataClassification, 0, @Message);
    END
    ELSE IF @UserClearance < @DataClassification
    BEGIN
        SET @ExportAllowed = 0;
        SET @Message = 'EXPORT BLOCKED: Insufficient clearance.';
        
        INSERT INTO AUDIT_LOG (ActionType, UserID, TableName, DataClassification, AccessGranted, Description)
        VALUES ('EXPORT_BLOCKED', @UserID, @TableName, @DataClassification, 0, @Message);
    END
    ELSE
    BEGIN
        SET @ExportAllowed = 1;
        SET @Message = 'Export allowed for ' + @TableName;
    END
END;
GO

PRINT '✓ Created sp_CheckExportAllowed (Flow Control - BONUS)';
GO

-- ============================================================
-- SECTION 5: ENCRYPTION PROCEDURES
-- ============================================================

-- Encrypt sensitive data
CREATE OR ALTER PROCEDURE sp_EncryptData
    @PlainText NVARCHAR(MAX),
    @EncryptedData VARBINARY(MAX) OUTPUT
AS
BEGIN
    OPEN SYMMETRIC KEY SRMS_SymmetricKey DECRYPTION BY CERTIFICATE SRMS_Certificate;
    SET @EncryptedData = EncryptByKey(Key_GUID('SRMS_SymmetricKey'), @PlainText);
    CLOSE SYMMETRIC KEY SRMS_SymmetricKey;
END;
GO

-- Decrypt sensitive data
CREATE OR ALTER PROCEDURE sp_DecryptData
    @EncryptedData VARBINARY(MAX),
    @UserID INT,
    @PlainText NVARCHAR(MAX) OUTPUT
AS
BEGIN
    DECLARE @UserClearance INT;
    
    SELECT @UserClearance = ClearanceLevel FROM USERS WHERE UserID = @UserID;
    
    -- Only users with sufficient clearance can decrypt
    IF @UserClearance < 2
    BEGIN
        SET @PlainText = '***ACCESS DENIED***';
        RETURN;
    END
    
    OPEN SYMMETRIC KEY SRMS_SymmetricKey DECRYPTION BY CERTIFICATE SRMS_Certificate;
    SET @PlainText = CONVERT(NVARCHAR(MAX), DecryptByKey(@EncryptedData));
    CLOSE SYMMETRIC KEY SRMS_SymmetricKey;
END;
GO

PRINT '✓ Created sp_EncryptData and sp_DecryptData (Encryption)';
GO

-- Insert Grade with Encryption
CREATE OR ALTER PROCEDURE sp_InsertGrade
    @StudentID INT,
    @CourseID INT,
    @GradeValue DECIMAL(5,2),
    @GradeLetter NVARCHAR(2),
    @EnteredByUserID INT,
    @Semester NVARCHAR(20),
    @Success BIT OUTPUT,
    @Message NVARCHAR(200) OUTPUT
AS
BEGIN
    DECLARE @UserRole NVARCHAR(20);
    DECLARE @UserClearance INT;
    DECLARE @InstructorID INT;
    DECLARE @CanWrite BIT;
    DECLARE @WriteMessage NVARCHAR(200);
    
    SELECT @UserRole = Role, @UserClearance = ClearanceLevel, 
           @InstructorID = LinkedID
    FROM USERS WHERE UserID = @EnteredByUserID;
    
    -- Check RBAC
    IF @UserRole NOT IN ('Admin', 'Instructor')
    BEGIN
        SET @Success = 0;
        SET @Message = 'Access denied. Only Admin/Instructor can enter grades.';
        RETURN;
    END
    
    -- Check MLS (No Write Down)
    EXEC sp_MLSWriteCheck @UserClearance, 3, @CanWrite OUTPUT, @WriteMessage OUTPUT;
    
    IF @CanWrite = 0
    BEGIN
        SET @Success = 0;
        SET @Message = @WriteMessage;
        RETURN;
    END
    
    -- Insert with encryption
    OPEN SYMMETRIC KEY SRMS_SymmetricKey DECRYPTION BY CERTIFICATE SRMS_Certificate;
    
    INSERT INTO GRADES (StudentID, StudentID_Encrypted, CourseID, GradeValue, GradeValue_Display, 
                        GradeLetter, EnteredBy, Semester, ClassificationLevel)
    VALUES (
        @StudentID,
        EncryptByKey(Key_GUID('SRMS_SymmetricKey'), CAST(@StudentID AS NVARCHAR(20))),
        @CourseID,
        EncryptByKey(Key_GUID('SRMS_SymmetricKey'), CAST(@GradeValue AS NVARCHAR(10))),
        @GradeValue,
        @GradeLetter,
        @InstructorID,
        @Semester,
        3  -- Secret classification
    );
    
    CLOSE SYMMETRIC KEY SRMS_SymmetricKey;
    
    SET @Success = 1;
    SET @Message = 'Grade inserted successfully.';
    
    INSERT INTO AUDIT_LOG (ActionType, TableName, UserID, Description, AccessGranted)
    VALUES ('INSERT', 'GRADES', @EnteredByUserID, 
            'Grade inserted for Student ' + CAST(@StudentID AS NVARCHAR(10)), 1);
END;
GO

PRINT '✓ Created sp_InsertGrade (with Encryption)';
GO

-- ============================================================
-- SECTION 6: PART B - ROLE REQUEST PROCEDURES
-- ============================================================

-- Submit Role Request (Student/TA)
CREATE OR ALTER PROCEDURE sp_SubmitRoleRequest
    @UserID INT,
    @RequestedRole NVARCHAR(20),
    @Reason NVARCHAR(MAX),
    @Comments NVARCHAR(MAX) = NULL,
    @Success BIT OUTPUT,
    @Message NVARCHAR(200) OUTPUT
AS
BEGIN
    DECLARE @CurrentRole NVARCHAR(20);
    DECLARE @CurrentClearance INT;
    DECLARE @RequestedClearance INT;
    DECLARE @Username NVARCHAR(50);
    DECLARE @PendingCount INT;
    
    SELECT 
        @Username = Username,
        @CurrentRole = Role,
        @CurrentClearance = ClearanceLevel
    FROM USERS WHERE UserID = @UserID;
    
    -- Validate: Cannot request same or lower role
    IF @CurrentRole = 'Admin'
    BEGIN
        SET @Success = 0;
        SET @Message = 'Admins cannot request role upgrades.';
        RETURN;
    END
    
    -- Valid upgrade paths: Student->TA, TA->Instructor
    IF NOT ((@CurrentRole = 'Student' AND @RequestedRole = 'TA') OR
            (@CurrentRole = 'TA' AND @RequestedRole = 'Instructor'))
    BEGIN
        SET @Success = 0;
        SET @Message = 'Invalid upgrade path. Student->TA or TA->Instructor only.';
        RETURN;
    END
    
    -- Check for existing pending requests
    SELECT @PendingCount = COUNT(*) 
    FROM ROLE_REQUESTS 
    WHERE UserID = @UserID AND Status = 'Pending';
    
    IF @PendingCount > 0
    BEGIN
        SET @Success = 0;
        SET @Message = 'You already have a pending role request.';
        RETURN;
    END
    
    -- Set requested clearance
    SET @RequestedClearance = CASE @RequestedRole
        WHEN 'TA' THEN 2
        WHEN 'Instructor' THEN 3
        ELSE @CurrentClearance
    END;
    
    -- Insert request
    INSERT INTO ROLE_REQUESTS (UserID, Username, CurrentRole, RequestedRole,
                              CurrentClearance, RequestedClearance, Reason, 
                              Comments, Status, DateSubmitted)
    VALUES (@UserID, @Username, @CurrentRole, @RequestedRole,
            @CurrentClearance, @RequestedClearance, @Reason,
            @Comments, 'Pending', GETDATE());
    
    SET @Success = 1;
    SET @Message = 'Role upgrade request submitted successfully.';
    
    INSERT INTO AUDIT_LOG (ActionType, UserID, Username, Description)
    VALUES ('ROLE_REQUEST_SUBMITTED', @UserID, @Username, 
            'Requested upgrade: ' + @CurrentRole + ' -> ' + @RequestedRole);
END;
GO

PRINT '✓ Created sp_SubmitRoleRequest (Part B - 5 marks)';
GO

-- Get Pending Role Requests (Admin Dashboard)
CREATE OR ALTER PROCEDURE sp_GetPendingRoleRequests
    @AdminUserID INT
AS
BEGIN
    DECLARE @AdminRole NVARCHAR(20);
    
    SELECT @AdminRole = Role FROM USERS WHERE UserID = @AdminUserID;
    
    IF @AdminRole != 'Admin'
    BEGIN
        RAISERROR('Access denied. Admin role required.', 16, 1);
        RETURN;
    END
    
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
    ORDER BY DateSubmitted ASC;
END;
GO

PRINT '✓ Created sp_GetPendingRoleRequests (Admin Dashboard)';
GO

-- Process Role Request (Admin Approve/Deny)
CREATE OR ALTER PROCEDURE sp_ProcessRoleRequest
    @RequestID INT,
    @AdminUserID INT,
    @Action NVARCHAR(10),  -- 'Approve' or 'Deny'
    @AdminComments NVARCHAR(MAX) = NULL,
    @Success BIT OUTPUT,
    @Message NVARCHAR(200) OUTPUT
AS
BEGIN
    DECLARE @AdminRole NVARCHAR(20);
    DECLARE @AdminUsername NVARCHAR(50);
    DECLARE @TargetUserID INT;
    DECLARE @RequestedRole NVARCHAR(20);
    DECLARE @RequestedClearance INT;
    DECLARE @CurrentStatus NVARCHAR(20);
    
    SELECT @AdminRole = Role, @AdminUsername = Username 
    FROM USERS WHERE UserID = @AdminUserID;
    
    -- Only Admin can process
    IF @AdminRole != 'Admin'
    BEGIN
        SET @Success = 0;
        SET @Message = 'Access denied. Admin role required.';
        RETURN;
    END
    
    -- Get request details
    SELECT 
        @TargetUserID = UserID,
        @RequestedRole = RequestedRole,
        @RequestedClearance = RequestedClearance,
        @CurrentStatus = Status
    FROM ROLE_REQUESTS WHERE RequestID = @RequestID;
    
    IF @TargetUserID IS NULL
    BEGIN
        SET @Success = 0;
        SET @Message = 'Request not found.';
        RETURN;
    END
    
    IF @CurrentStatus != 'Pending'
    BEGIN
        SET @Success = 0;
        SET @Message = 'Request already processed. Status: ' + @CurrentStatus;
        RETURN;
    END
    
    BEGIN TRANSACTION;
    
    IF @Action = 'Approve'
    BEGIN
        -- Update user's role and clearance
        UPDATE USERS
        SET Role = @RequestedRole,
            ClearanceLevel = @RequestedClearance,
            ModifiedDate = GETDATE(),
            ModifiedBy = @AdminUsername
        WHERE UserID = @TargetUserID;
        
        -- Update request status
        UPDATE ROLE_REQUESTS
        SET Status = 'Approved',
            DateProcessed = GETDATE(),
            ProcessedBy = @AdminUserID,
            ProcessedByUsername = @AdminUsername,
            AdminComments = @AdminComments
        WHERE RequestID = @RequestID;
        
        SET @Message = 'Request APPROVED. User upgraded to ' + @RequestedRole;
    END
    ELSE IF @Action = 'Deny'
    BEGIN
        -- Update request status only (no role change)
        UPDATE ROLE_REQUESTS
        SET Status = 'Denied',
            DateProcessed = GETDATE(),
            ProcessedBy = @AdminUserID,
            ProcessedByUsername = @AdminUsername,
            AdminComments = @AdminComments
        WHERE RequestID = @RequestID;
        
        SET @Message = 'Request DENIED. User role unchanged.';
    END
    ELSE
    BEGIN
        ROLLBACK TRANSACTION;
        SET @Success = 0;
        SET @Message = 'Invalid action. Use "Approve" or "Deny".';
        RETURN;
    END
    
    COMMIT TRANSACTION;
    SET @Success = 1;
    
    INSERT INTO AUDIT_LOG (ActionType, UserID, Username, Description)
    VALUES ('ROLE_REQUEST_' + UPPER(@Action) + 'D', @AdminUserID, @AdminUsername,
            'Request #' + CAST(@RequestID AS NVARCHAR(10)) + ' ' + LOWER(@Action) + 'd');
END;
GO

PRINT '✓ Created sp_ProcessRoleRequest (Part B - 5 marks)';
GO

-- ============================================================
-- SECTION 7: ADMIN USER MANAGEMENT
-- ============================================================

-- Create User (Admin only)
CREATE OR ALTER PROCEDURE sp_CreateUser
    @Username NVARCHAR(50),
    @Password NVARCHAR(100),
    @Role NVARCHAR(20),
    @AdminUserID INT,
    @NewUserID INT OUTPUT,
    @Message NVARCHAR(200) OUTPUT
AS
BEGIN
    DECLARE @AdminRole NVARCHAR(20);
    DECLARE @Salt VARBINARY(128);
    DECLARE @Hash VARBINARY(256);
    DECLARE @ClearanceLevel INT;
    
    SELECT @AdminRole = Role FROM USERS WHERE UserID = @AdminUserID;
    
    IF @AdminRole != 'Admin'
    BEGIN
        SET @Message = 'Access denied. Admin role required.';
        SET @NewUserID = 0;
        RETURN;
    END
    
    -- Check if username exists
    IF EXISTS (SELECT 1 FROM USERS WHERE Username = @Username)
    BEGIN
        SET @Message = 'Username already exists.';
        SET @NewUserID = 0;
        RETURN;
    END
    
    -- Set clearance based on role
    SET @ClearanceLevel = CASE @Role
        WHEN 'Admin' THEN 4
        WHEN 'Instructor' THEN 3
        WHEN 'TA' THEN 2
        WHEN 'Student' THEN 1
        ELSE 0
    END;
    
    -- Generate salt and hash password
    SET @Salt = CAST(NEWID() AS VARBINARY(128));
    SET @Hash = HASHBYTES('SHA2_256', @Password + CAST(@Salt AS NVARCHAR(256)));
    
    INSERT INTO USERS (Username, PasswordHash, PasswordSalt, Role, ClearanceLevel)
    VALUES (@Username, @Hash, @Salt, @Role, @ClearanceLevel);
    
    SET @NewUserID = SCOPE_IDENTITY();
    SET @Message = 'User created successfully. ID: ' + CAST(@NewUserID AS NVARCHAR(10));
    
    INSERT INTO AUDIT_LOG (ActionType, UserID, TableName, RecordID, Description)
    VALUES ('CREATE_USER', @AdminUserID, 'USERS', @NewUserID, 
            'Created user: ' + @Username + ' with role: ' + @Role);
END;
GO

PRINT '✓ Created sp_CreateUser (Admin Management)';
GO

-- ============================================================
-- SECTION 8: SUMMARY
-- ============================================================

PRINT '';
PRINT '═══════════════════════════════════════════════════════════════════';
PRINT '  STORED PROCEDURES - SUMMARY';
PRINT '═══════════════════════════════════════════════════════════════════';
PRINT '';
PRINT '  Authentication:';
PRINT '    • sp_UserLogin (with account locking)';
PRINT '';
PRINT '  MLS (Bell-LaPadula):';
PRINT '    • sp_MLSReadCheck (No Read Up - MANDATORY)';
PRINT '    • sp_MLSWriteCheck (No Write Down - BONUS)';
PRINT '    • sp_MLSAccessCheck (Combined check)';
PRINT '';
PRINT '  Inference Control:';
PRINT '    • sp_GetCourseStatistics (min 3 records)';
PRINT '';
PRINT '  Flow Control:';
PRINT '    • sp_CheckDataFlow (Downflow prevention)';
PRINT '    • sp_CheckExportAllowed (Block export - BONUS)';
PRINT '';
PRINT '  Encryption (AES-256):';
PRINT '    • sp_EncryptData';
PRINT '    • sp_DecryptData';
PRINT '    • sp_InsertGrade (encrypted)';
PRINT '';
PRINT '  Part B - Role Requests (10 marks):';
PRINT '    • sp_SubmitRoleRequest (5 marks)';
PRINT '    • sp_GetPendingRoleRequests (Admin)';
PRINT '    • sp_ProcessRoleRequest (5 marks)';
PRINT '';
PRINT '  Admin:';
PRINT '    • sp_CreateUser';
PRINT '';
PRINT '═══════════════════════════════════════════════════════════════════';
GO
