# Secure Student Records Management System (SRMS)



#### 1. Project Overview

The **Secure Student Records Management System (SRMS)** is a  database application designed to manage academic data while enforcing five core database security models. The system ensures strict access control, data confidentiality, integrity, and auditability across multiple user roles.

the **Secure Student Records Management System (SRMS)**. Below is the full documentation with structured sections, tables, and descriptions

The Secure Student Records Management System (SRMS) is a database application that implements five security models for managing academic data. It is built with a Python/Tkinter front-end, a Python back-end using pymssql, and a SQL Server database.

## Technology Stack

| Component  | Technology       |
| ---------- | ---------------- |
| Frontend   | Python Tkinter   |
| Backend    | Python, pymssql  |
| Database   | SQL Server       |
| Encryption | AES‑256, SHA‑256 |

## 2. SYSTEM ARCHITECTURE

The system follows a three‑layer architecture:

- **Presentation layer:** Tkinter GUI with role‑based dashboards
- **Application layer:** Python business logic that enforces all security policies
- **Data layer:** SQL Server with stored procedures, views, and encrypted data

(The original PDF includes an architecture diagram and an ERD with security labels; those are not reproducible in text.)

## 3. DATABASE SCHEMA

### 3.1 Entity Relationship Diagram (ERD)

The main entities are: USERS, STUDENT, INSTRUCTOR, COURSE, GRADES, ATTENDANCE, ROLE_REQUEST, AUDIT_LOG.

**Table Relationships**

| Relationship         | Cardinality |
| -------------------- | ----------- |
| INSTRUCTOR → COURSE  | 1:N         |
| STUDENT → GRADES     | 1:N         |
| STUDENT → ATTENDANCE | 1:N         |
| COURSE → GRADES      | 1:N         |
| COURSE → ATTENDANCE  | 1:N         |
| USERS → ROLE_REQUEST | 1:N         |

### 3.2 Table Structures

#### 3.2.1 USERS Table (Top Secret)

| Column         | Type           | Key | Description                               |
| -------------- | -------------- | --- | ----------------------------------------- |
| UserID         | INT            | PK  | Auto increment                            |
| Username       | NVARCHAR(50)   | UK  | Unique login                              |
| PasswordHash   | VARBINARY(256) |     | SHA‑256 hash                              |
| Salt           | VARBINARY(128) |     | Random salt                               |
| Role           | NVARCHAR(20)   |     | Admin / Instructor / TA / Student / Guest |
| ClearanceLevel | INT            |     | 0‑4 MLS level                             |

#### 3.2.2 STUDENT Table (Confidential)

| Column         | Type           | Key | Description    |
| -------------- | -------------- | --- | -------------- |
| StudentID      | INT            | PK  | Auto increment |
| FullName       | NVARCHAR(100)  |     | Student name   |
| Email          | NVARCHAR(100)  | UK  | Email address  |
| Phone          | VARBINARY(256) |     | AES Encrypted  |
| DOB            | DATE           |     | Date of birth  |
| Department     | NVARCHAR(50)   |     | Department     |
| ClearanceLevel | INT            |     | Default: 1     |

#### 3.2.3 INSTRUCTOR Table (Confidential)

| Column         | Type           | Key | Description     |
| -------------- | -------------- | --- | --------------- |
| InstructorID   | INT            | PK  | Auto increment  |
| FullName       | NVARCHAR(100)  |     | Instructor name |
| Email          | NVARCHAR(100)  | UK  | Email address   |
| Phone          | VARBINARY(256) |     | AES Encrypted   |
| Department     | NVARCHAR(50)   |     | Department      |
| ClearanceLevel | INT            |     | Default: 3      |

#### 3.2.4 COURSE Table (Unclassified)

| Column              | Type          | Key | Description    |
| ------------------- | ------------- | --- | -------------- |
| CourseID            | INT           | PK  | Auto increment |
| CourseCode          | NVARCHAR(20)  |     | Course code    |
| CourseName          | NVARCHAR(100) |     | Course title   |
| Description         | NVARCHAR(MAX) |     | Details        |
| PublicInfo          | NVARCHAR(MAX) |     | Guest visible  |
| InstructorID        | INT           | FK  | Instructor     |
| ClassificationLevel | INT           |     | Default: 1     |

#### 3.2.5 GRADES Table (Secret)

| Column              | Type           | Key | Description    |
| ------------------- | -------------- | --- | -------------- |
| GradeID             | INT            | PK  | Auto increment |
| StudentID           | INT            | FK  | Student        |
| CourseID            | INT            | FK  | Course         |
| GradeValue          | VARBINARY(256) |     | AES Encrypted  |
| DateEntered         | DATETIME       |     | Entry date     |
| EnteredBy           | INT            |     | Instructor ID  |
| ClassificationLevel | INT            |     | Default: 3     |

#### 3.2.6 ATTENDANCE Table (Secret)

| Column              | Type     | Key | Description             |
| ------------------- | -------- | --- | ----------------------- |
| AttendantID         | INT      | PK  | Auto increment          |
| StudentID           | INT      | FK  | Student                 |
| CourseID            | INT      | FK  | Course                  |
| Status              | BIT      |     | 1 = Present, 0 = Absent |
| DateRecorded        | DATETIME |     | Record date             |
| RecordedBy          | INT      |     | TA / Instructor ID      |
| ClassificationLevel | INT      |     | Default: 3              |

#### 3.2.7 ROLE_REQUEST Table (Secret)

| Column        | Type          | Key | Description                 |
| ------------- | ------------- | --- | --------------------------- |
| RequestID     | INT           | PK  | Auto increment              |
| UserID        | INT           | FK  | Requesting user             |
| CurrentRole   | NVARCHAR(20)  |     | Current role                |
| RequestedRole | NVARCHAR(20)  |     | Desired role                |
| Reason        | NVARCHAR(500) |     | Justification               |
| Status        | NVARCHAR(20)  |     | Pending / Approved / Denied |
| DateSubmitted | DATETIME      |     | Submission time             |
| ProcessedBy   | INT           |     | Admin ID                    |
| AdminComments | NVARCHAR(500) |     | Admin feedback              |

#### 3.2.8 AUDIT_LOG Table (Top Secret)

| Column        | Type          | Key | Description    |
| ------------- | ------------- | --- | -------------- |
| LogID         | INT           | PK  | Auto increment |
| ActionType    | NVARCHAR(50)  |     | Action type    |
| TableName     | NVARCHAR(50)  |     | Affected table |
| UserID        | INT           |     | Acting user    |
| UserRole      | NVARCHAR(20)  |     | User role      |
| Description   | NVARCHAR(MAX) |     | Details        |
| AccessGranted | BIT           |     | Success flag   |
| ActionDate    | DATETIME      |     | Timestamp      |

### 3.3 Security Classification Levels

| Level | Name         | Description                   |
| ----- | ------------ | ----------------------------- |
| 0     | Public       | Guest accessible              |
| 1     | Unclassified | Course info                   |
| 2     | Confidential | Student / Instructor profiles |
| 3     | Secret       | Grades, Attendance            |
| 4     | Top Secret   | Users, Audit logs             |

## 4. SECURITY MODELS

### 4.1 Access Control (RBAC)

Roles are arranged in a hierarchy (Admin → Instructor → TA → Student → Guest). Permissions are enforced through SQL Server roles and application‑level checks.

**Permission Matrix**

| Operation         | Admin | Instructor | TA  | Student | Guest |
| ----------------- | ----- | ---------- | --- | ------- | ----- |
| View own profile  | Y     | Y          | Y   | Y       | N     |
| Edit own profile  | Y     | Y          | Y   | N       | N     |
| View all students | Y     | Y          | Y*  | N       | N     |
| View grades       | Y     | Y          | N   | Y**     | N     |
| Edit grades       | Y     | Y          | N   | N       | N     |
| View attendance   | Y     | Y          | Y*  | Y**     | N     |
| Edit attendance   | Y     | Y          | Y*  | N       | N     |
| Manage users      | Y     | N          | N   | N       | N     |
| View courses      | Y     | Y          | Y   | Y       | Y***  |
| View audit log    | Y     | N          | N   | N       | N     |

*Y* = Yes, *N* = No  

* *Assigned courses only  
  ** Own data only  
  *** Public course information only

### 4.2 Inference Control

**Mechanism: Query Set Size Control**

- Minimum group size: **3 records**
- Aggregate queries returning fewer than 3 results are blocked.
- Restricted views automatically filter data by the user’s role assignment.
- This prevents users from inferring individual information from small result sets.

### 4.3 Flow Control

**Classification Flow**  
Data labelled “Secret” or “Top Secret” must not flow into a lower classification context. The system enforces this by:

- Disabling **Export** for Secret/Top Secret data
- Blocking **Copy/Paste** in the GUI for classified data
- Disabling **Print** for classified screens

### 4.4 Multilevel Security (MLS)

**Bell‑LaPadula Rules**

| Rule                | Description                                                  |
| ------------------- | ------------------------------------------------------------ |
| No Read Up (NRU)    | A subject cannot read data at a higher classification level. |
| No Write Down (NWD) | A subject cannot write data to a lower classification level. |

**Clearance Matrix**

| Role       | Clearance Level  | Can Read                |
| ---------- | ---------------- | ----------------------- |
| Admin      | 4 (Top Secret)   | All levels              |
| Instructor | 3 (Secret)       | Secret and below        |
| TA         | 2 (Confidential) | Confidential and below  |
| Student    | 1 (Restricted)   | Unclassified + own data |
| Guest      | 0 (Public)       | Unclassified only       |

### 4.5 Encryption

**Encrypted Fields**

| Table      | Column              | Algorithm           |
| ---------- | ------------------- | ------------------- |
| STUDENT    | Phone               | AES‑256             |
| STUDENT    | StudentID_Encrypted | AES‑256             |
| INSTRUCTOR | Phone               | AES‑256             |
| GRADES     | GradeValue          | AES‑256             |
| USERS      | PasswordHash        | SHA‑256 (with salt) |

Data is encrypted/decrypted via dedicated stored procedures (`sp_EncryptData`, `sp_DecryptData`). Direct database queries return only encrypted bytes.

## 5. USER ROLES AND PERMISSIONS

### 5.1 Default Test Accounts

| Username     | Password   | Role       | Clearance |
| ------------ | ---------- | ---------- | --------- |
| admin        | admin123   | Admin      | 4         |
| prof_smith   | prof123    | Instructor | 3         |
| prof_johnson | prof123    | Instructor | 3         |
| ta_williams  | ta123      | TA         | 2         |
| student1     | student123 | Student    | 1         |
| student2     | student123 | Student    | 1         |
| guest        | guest123   | Guest      | 0         |

### 5.2 Complete Access Matrix (partial view)

| Table   | Admin | Instructor | TA  | Student | Guest |
| ------- | ----- | ---------- | --- | ------- | ----- |
| STUDENT | CRUD  | R          | R*  | R (own) | DENY  |

(Other rows not fully extracted; the full matrix follows the pattern shown in the permission matrix above.)

## 6. ROLE UPGRADE REQUEST WORKFLOW

1. A Student (or lower‑role user) submits a role upgrade request, specifying the current role, requested role, and a reason.
2. The system validates the input and creates a record in the **ROLE_REQUEST** table with Status = “Pending”.
3. The Admin reviews pending requests in the dashboard.
4. Admin approves or denies each request.
   - **If approved:** The user’s role is updated in the USERS table, and the request status changes to “Approved”.
   - **If denied:** The request status is set to “Denied”, and the user’s role remains unchanged.

This workflow is implemented via stored procedures `sp_SubmitRoleRequest` and `sp_ApproveRoleRequest`.

## 7. DATABASE SETUP INSTRUCTIONS

1. Connect to SQL Server at `localhost,1433`.
2. Execute the following SQL scripts **in order**:
   - `sql/sqlserver_schema.sql`
   - `sql/sqlserver_roles.sql`
   - `sql/sqlserver_views.sql`
   - `sql/sqlserver_procedures.sql`
   - `sql/sqlserver_sample_data.sql`

## 8. TEST CASES

### 8.1 RBAC Tests

| ID         | Action                 | Expected | Status |
| ---------- | ---------------------- | -------- | ------ |
| TC‑RBAC‑01 | Guest views grades     | Denied   | Pass   |
| TC‑RBAC‑02 | Student edits grade    | Denied   | Pass   |
| TC‑RBAC‑03 | TA views grades        | Denied   | Pass   |
| TC‑RBAC‑04 | Instructor edits grade | Allowed  | Pass   |
| TC‑RBAC‑05 | Admin manages users    | Allowed  | Pass   |

### 8.2 Inference Control Tests

| ID        | Action                | Expected | Status |
| --------- | --------------------- | -------- | ------ |
| TC‑INF‑01 | Query with 2 records  | Blocked  | Pass   |
| TC‑INF‑02 | Query with 5 records  | Allowed  | Pass   |
| TC‑INF‑03 | TA views other course | Denied   | Pass   |

### 8.3 Flow Control Tests

| ID         | Action                | Expected | Status |
| ---------- | --------------------- | -------- | ------ |
| TC‑FLOW‑01 | Copy Secret to Public | Blocked  | Pass   |
| TC‑FLOW‑02 | Export grades as CSV  | Blocked  | Pass   |
| TC‑FLOW‑03 | Copy/paste in GUI     | Disabled | Pass   |

### 8.4 MLS Tests

| ID        | Action                        | Expected     | Status |
| --------- | ----------------------------- | ------------ | ------ |
| TC‑MLS‑01 | Student reads Secret          | Denied (NRU) | Pass   |
| TC‑MLS‑02 | Admin writes to Public        | Denied (NWD) | Pass   |
| TC‑MLS‑03 | Instructor reads Confidential | Allowed      | Pass   |

### 8.5 Encryption Tests

| ID        | Action               | Expected              | Status |
| --------- | -------------------- | --------------------- | ------ |
| TC‑ENC‑01 | View encrypted grade | Decrypted display     | Pass   |
| TC‑ENC‑02 | Direct DB query      | Shows encrypted bytes | Pass   |
| TC‑ENC‑03 | Password storage     | Hashed with salt      | Pass   |

### 8.6 Part B (Role Request) Tests

| ID       | Action                  | Expected         | Status |
| -------- | ----------------------- | ---------------- | ------ |
| TC‑PB‑01 | Student submits request | Saved as Pending | Pass   |
| TC‑PB‑02 | Admin approves          | Role updated     | Pass   |
| TC‑PB‑03 | Admin denies            | Role unchanged   | Pass   |

## 9. STORED PROCEDURES

| Procedure                | Purpose                            |
| ------------------------ | ---------------------------------- |
| `sp_UserLogin`           | Authenticate users                 |
| `sp_MLSReadCheck`        | Enforce No Read Up                 |
| `sp_MLSWriteCheck`       | Enforce No Write Down              |
| `sp_MLSAccessCheck`      | Combined MLS checks                |
| `sp_GetCourseStatistics` | Inference‑controlled statistics    |
| `sp_FlowControlCheck`    | Check data flow constraints        |
| `sp_CheckExportAllowed`  | Validate export permissions        |
| `sp_EncryptData`         | Encrypt using AES                  |
| `sp_DecryptData`         | Decrypt AES data                   |
| `sp_SubmitRoleRequest`   | Submit a role upgrade request      |
| `sp_ApproveRoleRequest`  | Admin approval/denial of a request |



#### 3. Technology Stack

| Component      | Technology                             |
| -------------- | -------------------------------------- |
| **Frontend**   | Python Tkinter                         |
| **Backend**    | Python, `pymssql`                      |
| **Database**   | Microsoft SQL Server                   |
| **Encryption** | AES-256 (Symmetric), SHA-256 (Hashing) |

---

## 4. System Architecture

The system follows a layered architecture:

1. **Presentation Layer**: Role-specific GUIs (Admin, Instructor, TA, Student, Guest)
2. **Application Layer**: Authentication, RBAC, Inference Control, Flow Control, MLS, Encryption
3. **Data Access Layer**: Stored Procedures & Secure Views
4. **Database Layer**: SQL Server tables (`STUDENT`, `INSTRUCTOR`, `COURSE`, `GRADES`, `ATTENDANCE`, `USERS`, `AUDIT_LOG`)
5. **Encryption Layer**: Master Key → Certificate → Symmetric Key (AES-256)

---

## 5. Database Schema & Entity Relationships

### Key Relationships

| Relationship              | Cardinality |
| ------------------------- | ----------- |
| `INSTRUCTOR` → `COURSE`   | 1:N         |
| `STUDENT` → `GRADES`      | 1:N         |
| `STUDENT` → `ATTENDANCE`  | 1:N         |
| `COURSE` → `GRADES`       | 1:N         |
| `COURSE` → `ATTENDANCE`   | 1:N         |
| `USERS` → `ROLE_REQUESTS` | 1:N         |

---

## 6. Table Structures

### 6.1 `USERS` Table (Top Secret)

| Column           | Type           | Key | Description                       |
| ---------------- | -------------- | --- | --------------------------------- |
| `UserID`         | INT            | PK  | Auto Increment                    |
| `Username`       | NVARCHAR(50)   | UK  | Unique login                      |
| `PasswordHash`   | VARBINARY(256) |     | SHA-256 hash                      |
| `Salt`           | VARBINARY(128) |     | Random salt                       |
| `Role`           | NVARCHAR(20)   |     | Admin/Instructor/TA/Student/Guest |
| `ClearanceLevel` | INT            |     | 0–4 MLS level                     |
| `IsActive`       | BIT            |     | Account status                    |
| `IsLocked`       | BIT            |     | Lock status                       |
| `LastLoginDate`  | DATETIME       |     | Last login timestamp              |

### 6.2 `STUDENT` Table (Confidential)

| Column           | Type           | Key | Description    |
| ---------------- | -------------- | --- | -------------- |
| `StudentID`      | INT            | PK  | Auto Increment |
| `FullName`       | NVARCHAR(100)  |     | Student name   |
| `Email`          | NVARCHAR(100)  | UK  | Email address  |
| `Phone`          | VARBINARY(256) |     | AES Encrypted  |
| `DOB`            | DATE           |     | Date of birth  |
| `Department`     | NVARCHAR(50)   |     | Department     |
| `ClearanceLevel` | INT            |     | Default: 1     |

### 6.3 `INSTRUCTOR` Table (Confidential)

| Column           | Type           | Key | Description     |
| ---------------- | -------------- | --- | --------------- |
| `InstructorID`   | INT            | PK  | Auto Increment  |
| `FullName`       | NVARCHAR(100)  |     | Instructor name |
| `Email`          | NVARCHAR(100)  | UK  | Email address   |
| `Phone`          | VARBINARY(256) |     | AES Encrypted   |
| `Department`     | NVARCHAR(50)   |     | Department      |
| `ClearanceLevel` | INT            |     | Default: 3      |

### 6.4 `COURSE` Table (Unclassified)

| Column                | Type          | Key | Description         |
| --------------------- | ------------- | --- | ------------------- |
| `CourseID`            | INT           | PK  | Auto Increment      |
| `CourseCode`          | NVARCHAR(20)  |     | Course code         |
| `CourseName`          | NVARCHAR(100) |     | Course title        |
| `Description`         | NVARCHAR(MAX) |     | Details             |
| `PublicInfo`          | NVARCHAR(MAX) |     | Guest visible       |
| `InstructorID`        | INT           | FK  | Assigned instructor |
| `ClassificationLevel` | INT           |     | Default: 1          |

### 6.5 `GRADES` Table (Secret)

| Column                | Type           | Key | Description    |
| --------------------- | -------------- | --- | -------------- |
| `GradeID`             | INT            | PK  | Auto Increment |
| `StudentID`           | INT            | FK  | Student        |
| `CourseID`            | INT            | FK  | Course         |
| `GradeValue`          | VARBINARY(256) |     | AES Encrypted  |
| `DateEntered`         | DATETIME       |     | Entry date     |
| `EnteredBy`           | INT            |     | Instructor ID  |
| `ClassificationLevel` | INT            |     | Default: 3     |

### 6.6 `ATTENDANCE` Table (Secret)

| Column                | Type     | Key | Description         |
| --------------------- | -------- | --- | ------------------- |
| `AttendanceID`        | INT      | PK  | Auto Increment      |
| `StudentID`           | INT      | FK  | Student             |
| `CourseID`            | INT      | FK  | Course              |
| `Status`              | BIT      |     | 1=Present, 0=Absent |
| `DateRecorded`        | DATETIME |     | Record date         |
| `RecordedBy`          | INT      |     | TA/Instructor ID    |
| `ClassificationLevel` | INT      |     | Default: 3          |

### 6.7 `ROLE_REQUESTS` Table (Secret)

| Column          | Type          | Key | Description             |
| --------------- | ------------- | --- | ----------------------- |
| `RequestID`     | INT           | PK  | Auto Increment          |
| `UserID`        | INT           | FK  | Requesting user         |
| `CurrentRole`   | NVARCHAR(20)  |     | Current role            |
| `RequestedRole` | NVARCHAR(20)  |     | Desired role            |
| `Reason`        | NVARCHAR(500) |     | Justification           |
| `Status`        | NVARCHAR(20)  |     | Pending/Approved/Denied |
| `DateSubmitted` | DATETIME      |     | Submission time         |
| `ProcessedBy`   | INT           |     | Admin ID                |
| `AdminComments` | NVARCHAR(500) |     | Admin feedback          |

### 6.8 `AUDIT_LOG` Table (Top Secret)

| Column          | Type          | Key | Description    |
| --------------- | ------------- | --- | -------------- |
| `LogID`         | INT           | PK  | Auto Increment |
| `ActionType`    | NVARCHAR(50)  |     | Action type    |
| `TableName`     | NVARCHAR(50)  |     | Affected table |
| `UserID`        | INT           |     | Acting user    |
| `UserRole`      | NVARCHAR(20)  |     | User role      |
| `Description`   | NVARCHAR(MAX) |     | Details        |
| `AccessGranted` | BIT           |     | Success flag   |
| `ActionDate`    | DATETIME      |     | Timestamp      |

---

## 7. Security Classification Levels

| Level | Name         | Description                 |
| ----- | ------------ | --------------------------- |
| 0     | Public       | Guest accessible            |
| 1     | Unclassified | Course information          |
| 2     | Confidential | Student/Instructor profiles |
| 3     | Secret       | Grades, Attendance          |
| 4     | Top Secret   | Users, Audit logs           |

---

## 8. Security Models Implementation Details

### 8.1 Access Control (RBAC)

- Role-based permissions enforced via SQL Server roles
- Granular CRUD operations per role
- GUI dynamically restricts navigation based on clearance

### 8.2 Inference Control

- **Mechanism**: Query Set Size Control
- **Rule**: Aggregate queries with `<3` records are blocked
- Prevents deduction of individual data from statistical outputs

### 8.3 Flow Control

- **Direction**: `TOP SECRET → SECRET → CONFIDENTIAL → UNCLASSIFIED`
- **Restriction**: Downward flow is blocked
- **GUI Bonuses**: Export disabled, Copy/Paste blocked, Print disabled for classified data

### 8.4 Multilevel Security (MLS)

- **Model**: Bell-LaPadula
- **Rules**: 
  - `No Read Up (NRU)`: Cannot read higher classification
  - `No Write Down (NWD)`: Cannot write to lower classification
- Enforced via stored procedures & clearance matrices

### 8.5 Encryption

- **Hierarchy**: `DATABASE MASTER KEY → SRMS_Certificate → SRMS_SymmetricKey (AES-256)`
- **Encrypted Fields**:
  
  | Table        | Column                     | Algorithm      |
  | ------------ | -------------------------- | -------------- |
  | `STUDENT`    | Phone, StudentID_Encrypted | AES-256        |
  | `INSTRUCTOR` | Phone                      | AES-256        |
  | `GRADES`     | GradeValue                 | AES-256        |
  | `USERS`      | PasswordHash               | SHA-256 + Salt |

---

## 9. User Roles & Permissions

### Default Test Accounts

| Username       | Password     | Role       | Clearance |
| -------------- | ------------ | ---------- | --------- |
| `admin`        | `admin123`   | Admin      | 4         |
| `prof_smith`   | `prof123`    | Instructor | 3         |
| `prof_johnson` | `prof123`    | Instructor | 3         |
| `ta_williams`  | `ta123`      | TA         | 2         |
| `student1`     | `student123` | Student    | 1         |
| `student2`     | `student123` | Student    | 1         |
| `guest`        | `guest123`   | Guest      | 0         |

### Permission Matrix

| Operation         | Admin | Instructor | TA  | Student | Guest |
| ----------------- | ----- | ---------- | --- | ------- | ----- |
| View own profile  | Y     | Y          | Y   | Y       | N     |
| Edit own profile  | Y     | Y          | Y   | N       | N     |
| View all students | Y     | Y          | Y*  | N       | N     |
| View grades       | Y     | Y          | N   | Y**     | N     |
| Edit grades       | Y     | Y          | N   | N       | N     |
| View attendance   | Y     | Y          | Y*  | Y**     | N     |
| Edit attendance   | Y     | Y          | Y*  | N       | N     |
| Manage users      | Y     | N          | N   | N       | N     |
| View courses      | Y     | Y          | Y   | Y       | Y***  |
| View audit log    | Y     | N          | N   | N       | N     |
|                   |       |            |     |         |       |

---

## 10. Role Upgrade Request Workflow (Part B)

1. **Student** submits request (Role + Reason)
2. **System** inserts into `ROLE_REQUESTS` with `Status='Pending'`
3. **Admin** views pending requests in dashboard
4. **Admin** approves or denies:
   -  **Approved**: `USERS.Role = NewRole`, `ROLE_REQUESTS.Status = 'Approved'`
   -  **Denied**: `ROLE_REQUESTS.Status = 'Denied'` (Role unchanged)
5. **Student** views updated status

---

## 11. Database Setup Instructions

1. Connect to SQL Server: `localhost, 1433`
2. Execute scripts in strict order:
   
   ```
   sql/sqlserver_schema.sql
   sql/sqlserver_roles.sql
   sql/sqlserver_views.sql
   sql/sqlserver_procedures.sql
   sql/sqlserver_sample_data.sql
   ```
3. Restore backup (optional): `SRMS_SecureDB.bak`

---

## 12. Test Cases

### RBAC Tests

| ID         | Action                 | Expected | Status |
| ---------- | ---------------------- | -------- | ------ |
| TC-RBAC-01 | Guest views grades     | Denied   | Pass   |
| TC-RBAC-02 | Student edits grade    | Denied   | Pass   |
| TC-RBAC-03 | TA views grades        | Denied   | Pass   |
| TC-RBAC-04 | Instructor edits grade | Allowed  | Pass   |
| TC-RBAC-05 | Admin manages users    | Allowed  | Pass   |

### Inference Control Tests

| ID        | Action                | Expected | Status |
| --------- | --------------------- | -------- | ------ |
| TC-INF-01 | Query with 2 records  | Blocked  | Pass   |
| TC-INF-02 | Query with 5 records  | Allowed  | Pass   |
| TC-INF-03 | TA views other course | Denied   | Pass   |

### Flow Control Tests

| ID         | Action                | Expected | Status |
| ---------- | --------------------- | -------- | ------ |
| TC-FLOW-01 | Copy Secret to Public | Blocked  | Pass   |
| TC-FLOW-02 | Export grades as CSV  | Blocked  | Pass   |
| TC-FLOW-03 | Copy/paste in GUI     | Disabled | Pass   |

### MLS Tests

| ID        | Action                        | Expected     | Status |
| --------- | ----------------------------- | ------------ | ------ |
| TC-MLS-01 | Student reads Secret          | Denied (NRU) | Pass   |
| TC-MLS-02 | Admin writes to Public        | Denied (NWD) | Pass   |
| TC-MLS-03 | Instructor reads Confidential | Allowed      | Pass   |

### Encryption Tests

| ID        | Action               | Expected              | Status |
| --------- | -------------------- | --------------------- | ------ |
| TC-ENC-01 | View encrypted grade | Decrypted display     | Pass   |
| TC-ENC-02 | Direct DB query      | Shows encrypted bytes | Pass   |
| TC-ENC-03 | Password storage     | Hashed with salt      | Pass   |

### Part B Tests

| ID       | Action                  | Expected         | Status |
| -------- | ----------------------- | ---------------- | ------ |
| TC-PB-01 | Student submits request | Saved as Pending | Pass   |
| TC-PB-02 | Admin approves          | Role updated     | Pass   |
| TC-PB-03 | Admin denies            | Role unchanged   | Pass   |

---

## 13. Stored Procedures

| Procedure                | Purpose                    |
| ------------------------ | -------------------------- |
| `sp_UserLogin`           | Authenticate user          |
| `sp_MLSReadCheck`        | No Read Up check           |
| `sp_MLSWriteCheck`       | No Write Down check        |
| `sp_MLSAccessCheck`      | Combined MLS check         |
| `sp_GetCourseStatistics` | Inference-controlled stats |
| `sp_FlowControlCheck`    | Check data flow            |
| `sp_CheckExportAllowed`  | Export permission          |
| `sp_EncryptData`         | Encrypt using AES          |
| `sp_DecryptData`         | Decrypt AES data           |
| `sp_SubmitRoleRequest`   | Part B request             |
| `sp_ApproveRoleRequest`  | Admin approval             |
| `sp_DenyRoleRequest`     | Admin denial               |

---






