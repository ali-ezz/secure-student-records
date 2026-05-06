# Secure Student Records

A security-first academic records management system for Python and SQL Server, built with role-based access controls, encryption, audit logging, and multilevel data protection.

## Overview

Secure Student Records provides a secure desktop-style interface for managing academic data across student, instructor, TA, and administrative roles. It is designed to demonstrate database security models, auditing, and confidentiality controls in an educational records environment.

## Problem Solved

Academic record systems often expose sensitive student data to too many users and lack enforced access controls. This repository addresses that gap by combining database security models with application-layer controls to protect records, grades, and personal information.

## Features

- Role-based access control (RBAC) with distinct user dashboards
- Multilevel security (MLS) enforcement for sensitive records
- Inference control to prevent sensitive aggregate disclosure
- Encrypted storage for personally identifiable information
- Audit logging of user and database activity
- SQL Server schema, roles, views, and stored procedures for secure access
- Desktop GUI launcher for Admin, Instructor, TA, Student, and Guest users

## Tech Stack

- Python 3
- Tkinter and ttkbootstrap for GUI
- Microsoft SQL Server backend
- `pyodbc` and `pymssql` for database connectivity
- `cryptography` and `bcrypt` for encryption and hashing
- `openpyxl` and `fpdf2` for reporting and exports

## Installation

1. Clone the repository:

```bash
git clone https://github.com/ali-ezz/secure-student-records.git
cd secure-student-records
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

4. Copy the environment example:

```bash
cp .env.example .env
```

5. Configure SQL Server credentials in `.env` and verify access.

6. Initialize the database using the SQL scripts in `sql/`.

## Usage

Run the application launcher:

```bash
python run.py
```

Or start the GUI directly:

```bash
python src/gui/main.py
```

The `run_all.sh` and `run_with_dbeaver.sh` helpers can assist with SQL and database tasks.

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
- `.env.example` — environment configuration template
- `src/` — application source code
- `database/` — local database support and backup artifacts
- `sql/` — SQL Server schema, roles, procedures, and sample data
- `tests/` — automated tests
- `.github/` — issue and pull request templates
- `assets/` — supporting images and diagrams

### Key source folders

- `src/gui/` — user interface screens, dashboards, and components
- `src/database/` — database connection and authentication logic
- `src/security/` — security enforcement and controls
- `src/utils/` — helper utilities and export tools

## Results

This repository is intended to be a secure reference implementation for academic record security. It focuses on enforceable access control, data classification, encryption, and auditability rather than a production deployment.

## Roadmap

- Add automated database provisioning and schema migration
- Improve environment variable support across the application
- Expand automated tests and coverage
- Add optional Docker support for local deployment
- Add configuration-driven role and policy management

## Credits

- Original implementation by the repository maintainer
- Security concepts inspired by RBAC, MLS, inference control, and secure database design

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
