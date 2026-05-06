"""
SRMS - SQL Server Database Connection
Provides connectivity to Microsoft SQL Server with security features
"""

import sys
import os
import hashlib
from datetime import datetime
from typing import Optional, Dict, Any, List

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# SQL Server connection options
try:
    import pyodbc
    HAS_PYODBC = True
except ImportError:
    HAS_PYODBC = False

try:
    import pymssql
    HAS_PYMSSQL = True
except ImportError:
    HAS_PYMSSQL = False


class SQLServerConnection:
    """SQL Server database connection manager."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize SQL Server connection.
        
        Args:
            config: Connection configuration dictionary
                - server: SQL Server hostname (default: localhost)
                - database: Database name (default: SRMS)
                - username: SQL Server username (optional for Windows Auth)
                - password: SQL Server password (optional for Windows Auth)
                - driver: ODBC driver name (default: ODBC Driver 17 for SQL Server)
                - trusted_connection: Use Windows Authentication (default: False)
        """
        self.config = config or {}
        self.server = self.config.get('server', 'localhost')
        self.database = self.config.get('database', 'SRMS')
        self.username = self.config.get('username', '')
        self.password = self.config.get('password', '')
        self.driver = self.config.get('driver', 'ODBC Driver 17 for SQL Server')
        self.trusted_connection = self.config.get('trusted_connection', False)
        
        self.connection = None
        self.cursor = None
    
    def connect(self) -> bool:
        """
        Establish database connection.
        
        Returns:
            True if connection successful
        """
        try:
            if HAS_PYODBC:
                return self._connect_pyodbc()
            elif HAS_PYMSSQL:
                return self._connect_pymssql()
            else:
                raise ImportError("No SQL Server driver available. Install pyodbc or pymssql")
        except Exception as e:
            print(f"Connection Error: {e}")
            return False
    
    def _connect_pyodbc(self) -> bool:
        """Connect using pyodbc."""
        if self.trusted_connection:
            # Windows Authentication
            conn_str = (
                f"DRIVER={{{self.driver}}};"
                f"SERVER={self.server};"
                f"DATABASE={self.database};"
                f"Trusted_Connection=yes;"
            )
        else:
            # SQL Server Authentication
            conn_str = (
                f"DRIVER={{{self.driver}}};"
                f"SERVER={self.server};"
                f"DATABASE={self.database};"
                f"UID={self.username};"
                f"PWD={self.password};"
            )
        
        self.connection = pyodbc.connect(conn_str)
        self.cursor = self.connection.cursor()
        print(f"Connected to SQL Server: {self.server}/{self.database}")
        return True
    
    def _connect_pymssql(self) -> bool:
        """Connect using pymssql."""
        self.connection = pymssql.connect(
            server=self.server,
            user=self.username,
            password=self.password,
            database=self.database
        )
        self.cursor = self.connection.cursor(as_dict=True)
        print(f"Connected to SQL Server: {self.server}/{self.database}")
        return True
    
    def disconnect(self):
        """Close database connection."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("Disconnected from SQL Server")
    
    def execute(self, query: str, params: tuple = None) -> Any:
        """
        Execute a SQL query.
        
        Args:
            query: SQL query string
            params: Query parameters
        
        Returns:
            Cursor for result iteration
        """
        if not self.connection:
            self.connect()
        
        if params:
            self.cursor.execute(query, params)
        else:
            self.cursor.execute(query)
        
        return self.cursor
    
    def execute_proc(self, proc_name: str, params: Dict = None) -> List[Dict]:
        """
        Execute a stored procedure.
        
        Args:
            proc_name: Stored procedure name
            params: Dictionary of parameters
        
        Returns:
            List of result rows as dictionaries
        """
        if not self.connection:
            self.connect()
        
        # Build parameter string
        if params:
            param_str = ', '.join([f"@{k}=?" for k in params.keys()])
            query = f"EXEC {proc_name} {param_str}"
            self.cursor.execute(query, tuple(params.values()))
        else:
            self.cursor.execute(f"EXEC {proc_name}")
        
        # Fetch results
        try:
            columns = [col[0] for col in self.cursor.description]
            return [dict(zip(columns, row)) for row in self.cursor.fetchall()]
        except:
            return []
    
    def fetch_one(self, query: str, params: tuple = None) -> Optional[Dict]:
        """Fetch single row as dictionary."""
        self.execute(query, params)
        row = self.cursor.fetchone()
        
        if row:
            columns = [col[0] for col in self.cursor.description]
            return dict(zip(columns, row))
        return None
    
    def fetch_all(self, query: str, params: tuple = None) -> List[Dict]:
        """Fetch all rows as list of dictionaries."""
        self.execute(query, params)
        columns = [col[0] for col in self.cursor.description]
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]
    
    def commit(self):
        """Commit transaction."""
        if self.connection:
            self.connection.commit()
    
    def rollback(self):
        """Rollback transaction."""
        if self.connection:
            self.connection.rollback()


class SQLServerUserModel:
    """User model for SQL Server with security features."""
    
    def __init__(self, db: SQLServerConnection):
        self.db = db
    
    def authenticate(self, username: str, password: str) -> Optional[Dict]:
        """
        Authenticate user using stored procedure.
        
        Args:
            username: Username
            password: Password
        
        Returns:
            User dictionary if successful, None otherwise
        """
        # Hash password (should match how it was stored)
        password_hash = hashlib.sha256(password.encode()).digest()
        
        result = self.db.execute_proc('sp_AuthenticateUser', {
            'username': username,
            'password_hash': password_hash
        })
        
        if result and result[0].get('success') == 1:
            return {
                'user_id': result[0]['user_id'],
                'username': result[0]['username'],
                'role': result[0]['role'],
                'clearance_level': result[0]['clearance_level']
            }
        return None
    
    def create_user(self, username: str, password: str, role: str, 
                    created_by_user_id: int) -> Dict:
        """
        Create new user using stored procedure.
        
        Args:
            username: Username
            password: Password
            role: User role
            created_by_user_id: Admin user ID creating this user
        
        Returns:
            Result dictionary
        """
        import os
        
        # Generate salt and hash password
        password_salt = os.urandom(32)
        password_hash = hashlib.pbkdf2_hmac(
            'sha256', password.encode(), password_salt, 100000
        )
        
        try:
            result = self.db.execute_proc('sp_CreateUser', {
                'username': username,
                'password_hash': password_hash,
                'password_salt': password_salt,
                'role': role,
                'created_by_user_id': created_by_user_id
            })
            self.db.commit()
            
            if result:
                return result[0]
            return {'error': 'Failed to create user'}
        except Exception as e:
            self.db.rollback()
            return {'error': str(e)}


class SQLServerGradeModel:
    """Grade model for SQL Server with MLS enforcement."""
    
    def __init__(self, db: SQLServerConnection):
        self.db = db
    
    def get_grades(self, user_id: int) -> List[Dict]:
        """
        Get grades with MLS filtering via stored procedure.
        
        Args:
            user_id: User requesting grades
        
        Returns:
            List of accessible grades
        """
        return self.db.execute_proc('sp_GetGrades_MLS', {'user_id': user_id})
    
    def insert_grade(self, student_id: int, course_id: int, 
                     grade_value: float, grade_letter: str,
                     entered_by_user_id: int) -> Dict:
        """
        Insert grade with encryption via stored procedure.
        
        Args:
            student_id: Student ID
            course_id: Course ID
            grade_value: Numeric grade
            grade_letter: Letter grade
            entered_by_user_id: Instructor user ID
        
        Returns:
            Result dictionary
        """
        try:
            result = self.db.execute_proc('sp_InsertGrade', {
                'student_id': student_id,
                'course_id': course_id,
                'grade_value': grade_value,
                'grade_letter': grade_letter,
                'entered_by_user_id': entered_by_user_id
            })
            self.db.commit()
            return result[0] if result else {'grade_id': None}
        except Exception as e:
            self.db.rollback()
            return {'error': str(e)}
    
    def get_statistics(self, course_id: int, user_id: int) -> Dict:
        """
        Get grade statistics with inference control.
        
        Args:
            course_id: Course ID
            user_id: User requesting stats
        
        Returns:
            Statistics dictionary
        """
        result = self.db.execute_proc('sp_GetGradeStatistics_Safe', {
            'course_id': course_id,
            'user_id': user_id,
            'min_count': 3
        })
        return result[0] if result else {}


class SQLServerRoleRequestModel:
    """Role request model for SQL Server."""
    
    def __init__(self, db: SQLServerConnection):
        self.db = db
    
    def submit_request(self, user_id: int, requested_role: str, 
                       reason: str) -> Dict:
        """Submit role upgrade request."""
        try:
            result = self.db.execute_proc('sp_SubmitRoleRequest', {
                'user_id': user_id,
                'requested_role': requested_role,
                'reason': reason
            })
            self.db.commit()
            return result[0] if result else {'error': 'Failed to submit'}
        except Exception as e:
            self.db.rollback()
            return {'error': str(e)}
    
    def process_request(self, request_id: int, admin_user_id: int,
                        approved: bool, notes: str = None) -> Dict:
        """Process role request (Admin only)."""
        try:
            result = self.db.execute_proc('sp_ProcessRoleRequest', {
                'request_id': request_id,
                'admin_user_id': admin_user_id,
                'approved': approved,
                'notes': notes
            })
            self.db.commit()
            return result[0] if result else {'error': 'Failed to process'}
        except Exception as e:
            self.db.rollback()
            return {'error': str(e)}
    
    def get_pending_requests(self) -> List[Dict]:
        """Get all pending role requests."""
        return self.db.fetch_all("""
            SELECT r.*, u.username 
            FROM ROLE_REQUESTS r
            JOIN USERS u ON r.user_id = u.user_id
            WHERE r.status = 'Pending'
            ORDER BY r.date_submitted
        """)


# Factory function for database connection
def get_sqlserver_connection(config: Dict = None) -> SQLServerConnection:
    """
    Get SQL Server connection instance.
    
    Args:
        config: Connection configuration
    
    Returns:
        SQLServerConnection instance
    """
    db = SQLServerConnection(config)
    db.connect()
    return db


# Example configuration
SQLSERVER_CONFIG = {
    'server': 'localhost',
    'database': 'SRMS',
    'username': 'sa',
    'password': 'YourPassword123!',
    'driver': 'ODBC Driver 17 for SQL Server',
    'trusted_connection': False  # Set to True for Windows Auth
}
