#!/usr/bin/env python3
"""
🚀 SRMS - Master Launcher (Python)
Starts all components with one command
"""

import os
import sys
import subprocess
import time
import signal
from pathlib import Path

# Project directory
PROJECT_DIR = Path(__file__).parent.absolute()
os.chdir(PROJECT_DIR)

# Colors
class Colors:
    BLUE = '\033[0;34m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    NC = '\033[0m'

# Global process list for cleanup
processes = []

def print_header():
    print(f"{Colors.BLUE}")
    print("=" * 50)
    print("  🔐 SRMS - Master Launcher")
    print("  Starting All Components...")
    print("=" * 50)
    print(f"{Colors.NC}\n")

def print_step(step, total, message):
    print(f"{Colors.GREEN}[{step}/{total}] {message}{Colors.NC}")

def start_docker():
    """Start SQL Server in Docker"""
    print_step(1, 5, "Starting SQL Server (Docker)...")
    
    # Check if container exists
    result = subprocess.run(['docker', 'ps', '-a'], capture_output=True, text=True)
    
    if 'sqlserver2022' in result.stdout:
        # Container exists, check if running
        if 'Up' not in result.stdout or 'sqlserver2022' not in subprocess.run(
            ['docker', 'ps'], capture_output=True, text=True
        ).stdout:
            print("  → Starting existing container...")
            subprocess.run(['docker', 'start', 'sqlserver2022'], 
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            print("  ✓ SQL Server already running")
    else:
        print("  → Creating new container...")
        subprocess.run([
            'docker', 'run',
            '-e', 'ACCEPT_EULA=Y',
            '-e', 'MSSQL_SA_PASSWORD=Srms@2024!',
            '-p', '1433:1433',
            '--name', 'sqlserver2022',
            '--hostname', 'sqlserver',
            '-d',
            'mcr.microsoft.com/mssql/server:2022-latest'
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    print("  → Waiting for SQL Server to be ready...")
    time.sleep(10)
    
    # Test connection
    try:
        test = subprocess.run([
            'docker', 'exec', 'sqlserver2022',
            '/opt/mssql-tools18/bin/sqlcmd',
            '-S', 'localhost', '-U', 'SA', '-P', 'Srms@2024!', '-C',
            '-Q', 'SELECT 1'
        ], capture_output=True, timeout=5)
        
        if test.returncode == 0:
            print(f"  {Colors.GREEN}✓ SQL Server is ready!{Colors.NC}")
        else:
            print(f"  {Colors.YELLOW}⚠ SQL Server connection test failed{Colors.NC}")
    except:
        print(f"  {Colors.YELLOW}⚠ Could not test SQL Server connection{Colors.NC}")
    
    print()

def start_dbeaver():
    """Open DBeaver with SQL files"""
    print_step(2, 5, "Starting DBeaver...")
    
    sql_files = [
        PROJECT_DIR / "sql/sqlserver_schema.sql",
        PROJECT_DIR / "sql/sqlserver_roles.sql",
        PROJECT_DIR / "sql/sqlserver_views.sql",
        PROJECT_DIR / "sql/sqlserver_procedures_fixed.sql",
        PROJECT_DIR / "sql/sqlserver_sample_data.sql",
    ]
    
    # Find DBeaver
    dbeaver_cmd = None
    for cmd in ['dbeaver', 'dbeaver-ce', '/snap/bin/dbeaver-ce']:
        try:
            subprocess.run([cmd, '--version'], 
                         capture_output=True, timeout=2)
            dbeaver_cmd = cmd
            break
        except:
            continue
    
    if dbeaver_cmd:
        print("  → Opening DBeaver with SQL files...")
        subprocess.Popen(
            [dbeaver_cmd] + [str(f) for f in sql_files if f.exists()],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
        print(f"  {Colors.GREEN}✓ DBeaver launched!{Colors.NC}")
    else:
        print(f"  {Colors.YELLOW}⚠ DBeaver not found (optional, skipping){Colors.NC}")
        print("    Install: sudo snap install dbeaver-ce")
    
    print()

def start_web_viewer():
    """Start Flask web database viewer"""
    print_step(3, 5, "Starting Web Database Viewer...")
    
    viewer_file = PROJECT_DIR / "db_viewer.py"
    
    if not viewer_file.exists():
        print(f"  {Colors.YELLOW}⚠ db_viewer.py not found (skipping){Colors.NC}\n")
        return None
    
    # Activate venv and start Flask
    venv_python = PROJECT_DIR / ".venv/bin/python"
    
    if not venv_python.exists():
        print(f"  {Colors.YELLOW}⚠ Virtual environment not found{Colors.NC}\n")
        return None
    
    print("  → Starting Flask server on http://localhost:5000...")
    
    process = subprocess.Popen(
        [str(venv_python), str(viewer_file)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True
    )
    
    time.sleep(2)
    
    if process.poll() is None:
        print(f"  {Colors.GREEN}✓ Web Viewer running at http://localhost:5000{Colors.NC}")
        print(f"    PID: {process.pid}")
        processes.append(process)
        print()
        return process
    else:
        print(f"  {Colors.YELLOW}⚠ Web Viewer failed to start{Colors.NC}\n")
        return None

def open_browser():
    """Open web browser"""
    print_step(4, 5, "Opening Web Browser...")
    
    try:
        subprocess.Popen(
            ['xdg-open', 'http://localhost:5000'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print(f"  {Colors.GREEN}✓ Browser opened!{Colors.NC}")
    except:
        print("  → Manually open: http://localhost:5000")
    
    print()

def start_gui():
    """Start main GUI application"""
    print_step(5, 5, "Starting SRMS GUI Application...")
    
    venv_python = PROJECT_DIR / ".venv/bin/python"
    main_script = PROJECT_DIR / "src/gui/main.py"
    
    print("  → Launching main application...\n")
    
    # Print summary
    print(f"{Colors.BLUE}")
    print("=" * 50)
    print("  ✅ All Components Started!")
    print("=" * 50)
    print()
    print("Running Services:")
    print("  🐳 SQL Server   : localhost:1433")
    print("  🌐 Web Viewer   : http://localhost:5000")
    print("  💾 DBeaver      : Opened (if installed)")
    print("  🖥️  GUI App      : Starting now...")
    print()
    print("Press Ctrl+C in GUI to stop all services")
    print("=" * 50)
    print(f"{Colors.NC}\n")
    
    # Run GUI (blocking)
    subprocess.run([str(venv_python), str(main_script)])

def cleanup():
    """Clean up processes"""
    print(f"\n{Colors.YELLOW}GUI closed. Cleaning up...{Colors.NC}")
    
    # Kill all child processes
    for process in processes:
        try:
            if process.poll() is None:
                process.terminate()
                process.wait(timeout=5)
                print("  ✓ Web Viewer stopped")
        except:
            pass
    
    # Ask about Docker
    try:
        response = input("Stop SQL Server container? (y/N): ").strip().lower()
        if response == 'y':
            subprocess.run(['docker', 'stop', 'sqlserver2022'],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("  ✓ SQL Server stopped")
        else:
            print("  → SQL Server still running (run: docker stop sqlserver2022)")
    except:
        pass
    
    print(f"\n{Colors.GREEN}✓ SRMS Launcher finished!{Colors.NC}")

def signal_handler(sig, frame):
    """Handle Ctrl+C"""
    cleanup()
    sys.exit(0)

def main():
    # Setup signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        print_header()
        start_docker()
        start_dbeaver()
        web_process = start_web_viewer()
        
        if web_process:
            time.sleep(1)
            open_browser()
        
        start_gui()
        cleanup()
        
    except Exception as e:
        print(f"{Colors.RED}Error: {e}{Colors.NC}")
        cleanup()
        sys.exit(1)

if __name__ == "__main__":
    main()
