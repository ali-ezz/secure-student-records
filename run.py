#!/usr/bin/env python3
"""
🚀 SRMS Launcher with DBeaver Integration
Opens DBeaver with all SQL files and runs the GUI application
"""

import os
import sys
import subprocess
import time
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.absolute()
SQL_DIR = PROJECT_DIR / "sql"

# SQL files to open (in order)
SQL_FILES = [
    "sqlserver_schema.sql",
    "sqlserver_roles.sql", 
    "sqlserver_views.sql",
    "sqlserver_procedures.sql",
    "sqlserver_sample_data.sql",
]

def print_header():
    print("\n" + "=" * 60)
    print("  🔐 SRMS - Secure Student Records Management System")
    print("  Database Tools + GUI Launcher")
    print("=" * 60 + "\n")

def find_dbeaver():
    """Find DBeaver executable"""
    possible_commands = [
        'dbeaver',
        'dbeaver-ce',
        '/usr/bin/dbeaver',
        '/snap/bin/dbeaver-ce',
    ]
    
    for cmd in possible_commands:
        try:
            subprocess.run([cmd, '--version'], 
                         stdout=subprocess.DEVNULL, 
                         stderr=subprocess.DEVNULL,
                         timeout=2)
            return cmd
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
    
    return None

def open_dbeaver():
    """Open DBeaver with SQL files"""
    dbeaver_cmd = find_dbeaver()
    
    if not dbeaver_cmd:
        print("⚠️  DBeaver not found!")
        print("   Install with: sudo snap install dbeaver-ce")
        print("   Continuing without DBeaver...\n")
        return False
    
    print(f"✓ Found DBeaver: {dbeaver_cmd}")
    
    # Get full paths to SQL files
    sql_paths = [str(SQL_DIR / sql_file) for sql_file in SQL_FILES if (SQL_DIR / sql_file).exists()]
    
    if not sql_paths:
        print("⚠️  No SQL files found in sql/ directory")
        return False
    
    print(f"✓ Opening {len(sql_paths)} SQL files in DBeaver...")
    
    try:
        # Open DBeaver with all SQL files
        subprocess.Popen(
            [dbeaver_cmd] + sql_paths,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
        
        for sql_file in SQL_FILES:
            print(f"  → {sql_file}")
        
        print("✓ DBeaver launched successfully!\n")
        time.sleep(2)  # Give DBeaver time to start
        return True
        
    except Exception as e:
        print(f"⚠️  Failed to launch DBeaver: {e}\n")
        return False

def run_gui():
    """Run the SRMS GUI application"""
    print("✓ Starting SRMS GUI Application...\n")
    
    # Activate venv and run
    venv_python = PROJECT_DIR / ".venv" / "bin" / "python"
    main_script = PROJECT_DIR / "src" / "gui" / "main.py"
    
    if not venv_python.exists():
        print("⚠️  Virtual environment not found!")
        print("   Run: python3 -m venv .venv")
        print("   Then: source .venv/bin/activate && pip install -r requirements.txt")
        return False
    
    try:
        # Run the GUI (blocking)
        subprocess.run([str(venv_python), str(main_script)])
        print("\n✓ Application closed.")
        return True
        
    except KeyboardInterrupt:
        print("\n⚠️  Application interrupted by user.")
        return False
    except Exception as e:
        print(f"\n❌ Error running application: {e}")
        return False

def main():
    print_header()
    
    # Open DBeaver in background
    open_dbeaver()
    
    # Run GUI (foreground)
    run_gui()
    
    print("\n" + "=" * 60)
    print("  👋 Thank you for using SRMS!")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Launcher interrupted.\n")
        sys.exit(0)
