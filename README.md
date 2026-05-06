# Secure Student Records Management System (SRMS)

Secure Student Records Management System (SRMS) is a security-first academic records application built for managing student, instructor, and course data with strict access control, encryption, audit logging, and multilevel data protection.

## Overview

SRMS provides a desktop-grade Python GUI with a SQL Server backend and secure database policies. It is designed for environments where role-based access control, data confidentiality, and auditability are required.

The project demonstrates:

- Role-based access control (RBAC)
- Multilevel security (MLS) enforcement
- Inference control for sensitive aggregates
- Encrypted personal data storage
- Audit logging and secure workflows
- A Tkinter GUI for Admin, Instructor, TA, Student, and Guest users

## Features

- Secure authentication and role-aware dashboards
- Database security models: RBAC, MLS, inference control, flow control, and encryption
- SQL Server schema, roles, views, stored procedures, and sample data
- Data classification for student, instructor, course, grades, attendance, and audit records
- Template files and documentation for repository professionalism

## Tech Stack

| Component | Technology |
| --- | --- |
| Application | Python 3 |
| GUI | Tkinter, ttkbootstrap |
| Database | Microsoft SQL Server |
| Database Drivers | pymssql, pyodbc |
| Encryption | cryptography, bcrypt |
| Reporting | openpyxl, fpdf2 |

## Installation

1. Clone the repository:

```bash
git clone https://github.com/ali-ezz/Data-Security-Secure-Student-Records-Management-System-SRMS-.git
cd Data-Security-Secure-Student-Records-Management-System-SRMS-
```

2. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Copy the example environment file:

```bash
cp .env.example .env
```

5. Configure SQL Server credentials in `.env` if needed.

6. Prepare the database schema and sample data using the SQL scripts in `sql/`.

## Usage

- Start the application launcher:

```bash
python run.py
```

- Or run the GUI directly:

```bash
python src/gui/main.py
```

- Use the bundled `run_all.sh` or `run_with_dbeaver.sh` for SQL and database workflow assistance.

## Environment Variables

Use `.env.example` as a template for local configuration.

- `SQLSERVER_HOST`
- `SQLSERVER_PORT`
- `SQLSERVER_DATABASE`
- `SQLSERVER_USER`
- `SQLSERVER_PASSWORD`
- `DATABASE_TYPE`

## Project Structure

- `README.md` — project documentation
- `requirements.txt` — Python dependency list
- `.gitignore` — ignored files for git
- `.env.example` — environment configuration example
- `src/` — application source code
- `database/` — local SQLite support and backup database files
- `sql/` — SQL Server schema, security, procedures, and sample data
- `tests/` — automated repository tests
- `.github/` — issue and pull request templates
- `assets/screenshots/` — placeholder for screenshot assets

### Key source folders

- `src/gui/` — GUI screens, dashboards, and components
- `src/database/` — database connection and authentication logic
- `src/security/` — security modules and enforcement logic
- `src/utils/` — helper utilities and export tools

## Results

This repository is structured to support a secure student record management system with clearly defined roles, sensitive data classification, and audit controls. It aims to demonstrate best practices for repository documentation and security architecture in an educational or proof-of-concept setting.

## Future Improvements

- Add automated database provisioning and migration scripts
- Add configurable environment variable support in the application
- Add complete cross-platform installation instructions
- Add a larger automated test suite and coverage reports
- Add optional Docker container support
- Add secure deployment and continuous integration tooling

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
