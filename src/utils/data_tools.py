"""
SRMS - Data Import/Export and Email Notifications
Tools for data management and communication
"""

import sys
import os
import csv
import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

try:
    import ttkbootstrap as ttk
    from ttkbootstrap.constants import *
    HAS_TTKBOOTSTRAP = True
except ImportError:
    HAS_TTKBOOTSTRAP = False

from src.database.connection import get_database


class DataImportWizard:
    """Wizard for importing data from CSV/JSON files."""
    
    def __init__(self, parent, table_name: str, columns: list, on_complete=None):
        self.parent = parent
        self.table_name = table_name
        self.columns = columns
        self.on_complete = on_complete
        self.db = get_database()
        
        self.imported_data = []
        self._create_wizard()
    
    def _create_wizard(self):
        """Create import wizard dialog."""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title(f"📥 Import Data - {self.table_name}")
        self.dialog.geometry("600x500")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Notebook for steps
        self.notebook = ttk.Notebook(self.dialog)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Step 1: Select file
        self._create_step1()
        
        # Step 2: Preview data
        self._create_step2()
        
        # Step 3: Confirm import
        self._create_step3()
    
    def _create_step1(self):
        """Create file selection step."""
        step1 = ttk.Frame(self.notebook)
        self.notebook.add(step1, text="1. Select File")
        
        ttk.Label(step1, text="📁 Select a CSV or JSON file to import",
                  font=('Segoe UI', 12, 'bold')).pack(pady=20)
        
        ttk.Label(step1, text=f"Target Table: {self.table_name}").pack()
        ttk.Label(step1, text=f"Expected Columns: {', '.join(self.columns)}").pack(pady=10)
        
        file_frame = ttk.Frame(step1)
        file_frame.pack(pady=20)
        
        self.file_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.file_var, width=40).pack(side=tk.LEFT, padx=5)
        
        if HAS_TTKBOOTSTRAP:
            ttk.Button(file_frame, text="Browse", command=self._browse_file,
                       bootstyle="info").pack(side=tk.LEFT)
        else:
            ttk.Button(file_frame, text="Browse", command=self._browse_file).pack(side=tk.LEFT)
        
        if HAS_TTKBOOTSTRAP:
            ttk.Button(step1, text="Next →", command=self._load_preview,
                       bootstyle="primary").pack(pady=20)
        else:
            ttk.Button(step1, text="Next", command=self._load_preview).pack(pady=20)
    
    def _create_step2(self):
        """Create data preview step."""
        step2 = ttk.Frame(self.notebook)
        self.notebook.add(step2, text="2. Preview")
        
        ttk.Label(step2, text="📋 Preview imported data",
                  font=('Segoe UI', 12, 'bold')).pack(pady=10)
        
        # Preview tree
        self.preview_tree = ttk.Treeview(step2, columns=self.columns, show='headings', height=12)
        for col in self.columns:
            self.preview_tree.heading(col, text=col)
            self.preview_tree.column(col, width=100)
        self.preview_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.preview_status = tk.StringVar(value="")
        ttk.Label(step2, textvariable=self.preview_status).pack()
        
        btn_frame = ttk.Frame(step2)
        btn_frame.pack(pady=10)
        
        if HAS_TTKBOOTSTRAP:
            ttk.Button(btn_frame, text="← Back", command=lambda: self.notebook.select(0),
                       bootstyle="secondary").pack(side=tk.LEFT, padx=5)
            ttk.Button(btn_frame, text="Import →", command=self._confirm_import,
                       bootstyle="success").pack(side=tk.LEFT, padx=5)
        else:
            ttk.Button(btn_frame, text="Back", command=lambda: self.notebook.select(0)).pack(side=tk.LEFT, padx=5)
            ttk.Button(btn_frame, text="Import", command=self._confirm_import).pack(side=tk.LEFT, padx=5)
    
    def _create_step3(self):
        """Create confirmation step."""
        step3 = ttk.Frame(self.notebook)
        self.notebook.add(step3, text="3. Complete")
        
        self.complete_frame = ttk.Frame(step3)
        self.complete_frame.pack(expand=True)
        
        ttk.Label(self.complete_frame, text="✅", font=('Segoe UI', 48)).pack()
        
        self.complete_label = ttk.Label(self.complete_frame, text="Import Complete!",
                                         font=('Segoe UI', 16, 'bold'))
        self.complete_label.pack(pady=10)
        
        self.complete_details = ttk.Label(self.complete_frame, text="")
        self.complete_details.pack()
        
        if HAS_TTKBOOTSTRAP:
            ttk.Button(self.complete_frame, text="Close", command=self.dialog.destroy,
                       bootstyle="primary").pack(pady=20)
        else:
            ttk.Button(self.complete_frame, text="Close", command=self.dialog.destroy).pack(pady=20)
    
    def _browse_file(self):
        """Browse for import file."""
        filename = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            self.file_var.set(filename)
    
    def _load_preview(self):
        """Load and preview file data."""
        filename = self.file_var.get()
        if not filename:
            messagebox.showerror("Error", "Please select a file")
            return
        
        try:
            if filename.endswith('.csv'):
                self._load_csv(filename)
            elif filename.endswith('.json'):
                self._load_json(filename)
            else:
                messagebox.showerror("Error", "Unsupported file format")
                return
            
            # Show preview
            for item in self.preview_tree.get_children():
                self.preview_tree.delete(item)
            
            for row in self.imported_data[:50]:  # Show first 50
                values = [row.get(col, '') for col in self.columns]
                self.preview_tree.insert('', 'end', values=values)
            
            self.preview_status.set(f"Loaded {len(self.imported_data)} records")
            self.notebook.select(1)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {e}")
    
    def _load_csv(self, filename):
        """Load CSV file."""
        self.imported_data = []
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.imported_data.append(row)
    
    def _load_json(self, filename):
        """Load JSON file."""
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                self.imported_data = data
            else:
                self.imported_data = [data]
    
    def _confirm_import(self):
        """Import data to database."""
        if not self.imported_data:
            messagebox.showerror("Error", "No data to import")
            return
        
        success = 0
        failed = 0
        
        for row in self.imported_data:
            try:
                cols = ', '.join(self.columns)
                placeholders = ', '.join(['?' for _ in self.columns])
                values = [row.get(col, None) for col in self.columns]
                
                self.db.execute(f"INSERT INTO {self.table_name} ({cols}) VALUES ({placeholders})", tuple(values))
                success += 1
            except Exception as e:
                failed += 1
        
        self.db.commit()
        
        self.complete_details.config(text=f"Successfully imported: {success}\nFailed: {failed}")
        self.notebook.select(2)
        
        if self.on_complete:
            self.on_complete()


class DataExportWizard:
    """Wizard for exporting data to various formats."""
    
    def __init__(self, parent, data: list, columns: list, title: str = "Export Data"):
        self.parent = parent
        self.data = data
        self.columns = columns
        self.title = title
        
        self._create_dialog()
    
    def _create_dialog(self):
        """Create export dialog."""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title(f"📤 {self.title}")
        self.dialog.geometry("450x350")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        main = ttk.Frame(self.dialog)
        main.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        ttk.Label(main, text="📤 Export Options", font=('Segoe UI', 14, 'bold')).pack(pady=10)
        ttk.Label(main, text=f"Records to export: {len(self.data)}").pack()
        
        # Format selection
        format_frame = ttk.Labelframe(main, text="Export Format")
        format_frame.pack(fill=tk.X, pady=15)
        
        self.format_var = tk.StringVar(value="csv")
        
        formats = [
            ("CSV (Comma Separated)", "csv"),
            ("JSON (JavaScript Object Notation)", "json"),
            ("Text (Tab Separated)", "txt"),
            ("HTML (Web Page)", "html")
        ]
        
        for text, value in formats:
            ttk.Radiobutton(format_frame, text=text, variable=self.format_var, value=value).pack(anchor='w', padx=10, pady=3)
        
        # Options
        options_frame = ttk.Labelframe(main, text="Options")
        options_frame.pack(fill=tk.X, pady=10)
        
        self.include_headers = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Include column headers", 
                        variable=self.include_headers).pack(anchor='w', padx=10)
        
        # Buttons
        btn_frame = ttk.Frame(main)
        btn_frame.pack(pady=20)
        
        if HAS_TTKBOOTSTRAP:
            ttk.Button(btn_frame, text="📁 Export", command=self._export,
                       bootstyle="success").pack(side=tk.LEFT, padx=10)
            ttk.Button(btn_frame, text="Cancel", command=self.dialog.destroy,
                       bootstyle="secondary").pack(side=tk.LEFT)
        else:
            ttk.Button(btn_frame, text="Export", command=self._export).pack(side=tk.LEFT, padx=10)
            ttk.Button(btn_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.LEFT)
    
    def _export(self):
        """Export data to file."""
        fmt = self.format_var.get()
        
        extensions = {'csv': '.csv', 'json': '.json', 'txt': '.txt', 'html': '.html'}
        
        filename = filedialog.asksaveasfilename(
            defaultextension=extensions.get(fmt, '.csv'),
            filetypes=[(f"{fmt.upper()} files", f"*{extensions.get(fmt, '.csv')}"), ("All files", "*.*")]
        )
        
        if not filename:
            return
        
        try:
            if fmt == 'csv':
                self._export_csv(filename)
            elif fmt == 'json':
                self._export_json(filename)
            elif fmt == 'txt':
                self._export_txt(filename)
            elif fmt == 'html':
                self._export_html(filename)
            
            messagebox.showinfo("Success", f"Data exported to {filename}")
            self.dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {e}")
    
    def _export_csv(self, filename):
        """Export to CSV."""
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if self.include_headers.get():
                writer.writerow(self.columns)
            for row in self.data:
                if isinstance(row, dict):
                    writer.writerow([row.get(col, '') for col in self.columns])
                else:
                    writer.writerow(row)
    
    def _export_json(self, filename):
        """Export to JSON."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, default=str)
    
    def _export_txt(self, filename):
        """Export to tab-separated text."""
        with open(filename, 'w', encoding='utf-8') as f:
            if self.include_headers.get():
                f.write('\t'.join(self.columns) + '\n')
            for row in self.data:
                if isinstance(row, dict):
                    f.write('\t'.join(str(row.get(col, '')) for col in self.columns) + '\n')
                else:
                    f.write('\t'.join(str(v) for v in row) + '\n')
    
    def _export_html(self, filename):
        """Export to HTML table."""
        html = [
            '<!DOCTYPE html>',
            '<html><head>',
            '<style>',
            'table { border-collapse: collapse; width: 100%; }',
            'th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }',
            'th { background-color: #4CAF50; color: white; }',
            'tr:nth-child(even) { background-color: #f2f2f2; }',
            '</style></head><body>',
            f'<h2>{self.title}</h2>',
            f'<p>Exported: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>',
            '<table>',
        ]
        
        if self.include_headers.get():
            html.append('<tr>' + ''.join(f'<th>{col}</th>' for col in self.columns) + '</tr>')
        
        for row in self.data:
            if isinstance(row, dict):
                cells = ''.join(f'<td>{row.get(col, "")}</td>' for col in self.columns)
            else:
                cells = ''.join(f'<td>{v}</td>' for v in row)
            html.append(f'<tr>{cells}</tr>')
        
        html.extend(['</table></body></html>'])
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(html))


class EmailNotificationManager:
    """Email notification system (simulation)."""
    
    def __init__(self):
        self.email_log = []
        self.templates = {
            'grade_posted': {
                'subject': '📊 New Grade Posted',
                'body': 'Your grade for {course} has been posted. Please login to view your results.'
            },
            'role_approved': {
                'subject': '✅ Role Request Approved',
                'body': 'Your role upgrade request has been approved. You now have {role} access.'
            },
            'role_denied': {
                'subject': '❌ Role Request Denied',
                'body': 'Your role upgrade request has been denied. Reason: {reason}'
            },
            'password_changed': {
                'subject': '🔒 Password Changed',
                'body': 'Your password has been successfully changed. If you did not make this change, please contact admin.'
            },
            'announcement': {
                'subject': '📢 {title}',
                'body': '{content}'
            },
            'attendance_alert': {
                'subject': '⚠️ Attendance Alert',
                'body': 'You have been marked absent for {course} on {date}. If this is incorrect, please contact your instructor.'
            }
        }
    
    def send_email(self, recipient: str, template_name: str, params: dict = None) -> dict:
        """
        Send email notification (simulated).
        
        Args:
            recipient: Email address
            template_name: Template to use
            params: Template parameters
        
        Returns:
            Send result
        """
        params = params or {}
        template = self.templates.get(template_name)
        
        if not template:
            return {'success': False, 'error': 'Template not found'}
        
        subject = template['subject'].format(**params)
        body = template['body'].format(**params)
        
        # Simulate sending
        email_record = {
            'id': len(self.email_log) + 1,
            'recipient': recipient,
            'subject': subject,
            'body': body,
            'sent_at': datetime.now().isoformat(),
            'status': 'sent'
        }
        
        self.email_log.append(email_record)
        
        return {'success': True, 'email_id': email_record['id']}
    
    def get_email_log(self, limit: int = 50) -> list:
        """Get recent email log."""
        return self.email_log[-limit:]
    
    def send_bulk_notification(self, recipients: list, template_name: str, params: dict = None) -> dict:
        """Send notification to multiple recipients."""
        success = 0
        failed = 0
        
        for recipient in recipients:
            result = self.send_email(recipient, template_name, params)
            if result['success']:
                success += 1
            else:
                failed += 1
        
        return {'sent': success, 'failed': failed}


class SearchManager:
    """Global search across all data."""
    
    def __init__(self):
        self.db = get_database()
    
    def search(self, query: str, current_role: str = 'Admin') -> dict:
        """
        Search across all accessible data.
        
        Args:
            query: Search query
            current_role: User's role for access control
        
        Returns:
            Search results grouped by type
        """
        query = f"%{query}%"
        results = {
            'students': [],
            'courses': [],
            'users': [],
            'announcements': []
        }
        
        # Search students (Admin/Instructor only)
        if current_role in ['Admin', 'Instructor']:
            students = self.db.fetch_all("""
                SELECT student_id, full_name, email, department FROM STUDENT
                WHERE full_name LIKE ? OR email LIKE ? OR department LIKE ?
                LIMIT 10
            """, (query, query, query))
            results['students'] = [dict(s) for s in students]
        
        # Search courses (All authenticated users)
        if current_role != 'Guest':
            courses = self.db.fetch_all("""
                SELECT course_id, course_code, course_name, description FROM COURSE
                WHERE course_code LIKE ? OR course_name LIKE ? OR description LIKE ?
                LIMIT 10
            """, (query, query, query))
            results['courses'] = [dict(c) for c in courses]
        
        # Search users (Admin only)
        if current_role == 'Admin':
            users = self.db.fetch_all("""
                SELECT user_id, username, role FROM USERS
                WHERE username LIKE ?
                LIMIT 10
            """, (query,))
            results['users'] = [dict(u) for u in users]
        
        # Search announcements
        announcements = self.db.fetch_all("""
            SELECT announcement_id, title, content FROM ANNOUNCEMENTS
            WHERE title LIKE ? OR content LIKE ?
            LIMIT 10
        """, (query, query))
        results['announcements'] = [dict(a) for a in announcements]
        
        # Count total results
        results['total'] = sum(len(v) for v in results.values() if isinstance(v, list))
        
        return results


class BackupManager:
    """Database backup and restore manager."""
    
    def __init__(self):
        self.db = get_database()
        self.backup_dir = 'backups'
    
    def create_backup(self, filename: str = None) -> dict:
        """Create database backup."""
        import shutil
        
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
        
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"srms_backup_{timestamp}.db"
        
        backup_path = os.path.join(self.backup_dir, filename)
        
        try:
            shutil.copy('database/srms.db', backup_path)
            return {
                'success': True,
                'path': backup_path,
                'size': os.path.getsize(backup_path),
                'created': datetime.now().isoformat()
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def list_backups(self) -> list:
        """List available backups."""
        if not os.path.exists(self.backup_dir):
            return []
        
        backups = []
        for f in os.listdir(self.backup_dir):
            if f.endswith('.db'):
                path = os.path.join(self.backup_dir, f)
                backups.append({
                    'filename': f,
                    'path': path,
                    'size': os.path.getsize(path),
                    'modified': datetime.fromtimestamp(os.path.getmtime(path)).isoformat()
                })
        
        return sorted(backups, key=lambda x: x['modified'], reverse=True)
    
    def restore_backup(self, backup_path: str) -> dict:
        """Restore database from backup."""
        import shutil
        
        if not os.path.exists(backup_path):
            return {'success': False, 'error': 'Backup file not found'}
        
        try:
            # Create safety backup first
            self.create_backup(f"pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
            
            shutil.copy(backup_path, 'database/srms.db')
            return {'success': True, 'restored_from': backup_path}
        except Exception as e:
            return {'success': False, 'error': str(e)}


# Global instances
_email_manager = None
_search_manager = None
_backup_manager = None

def get_email_manager() -> EmailNotificationManager:
    global _email_manager
    if _email_manager is None:
        _email_manager = EmailNotificationManager()
    return _email_manager

def get_search_manager() -> SearchManager:
    global _search_manager
    if _search_manager is None:
        _search_manager = SearchManager()
    return _search_manager

def get_backup_manager() -> BackupManager:
    global _backup_manager
    if _backup_manager is None:
        _backup_manager = BackupManager()
    return _backup_manager
