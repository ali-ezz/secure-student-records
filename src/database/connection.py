"""
SRMS - Database Connection Manager
Supports both SQLite and SQL Server backends
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from config import DATABASE_PATH

# =================================================================
# DATABASE CONFIGURATION - CHANGE HERE TO SWITCH BACKENDS
# =================================================================

# Options: 'sqlite' or 'sqlserver'
DATABASE_TYPE = 'sqlserver'

# SQL Server connection settings
SQLSERVER_CONFIG = {
    'server': 'localhost',
    'port': 1433,
    'database': 'SRMS_SecureDB',
    'user': 'SA',
    'password': 'Srms@2024!',
}

# =================================================================


class SQLServerConnection:
    """
    SQL Server database connection manager using pymssql.
    
    Features:
    - Direct connection to SQL Server
    - Stored procedure execution
    - Transaction management
    """
    
    _instance = None
    _connection = None
    
    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize connection."""
        if SQLServerConnection._connection is None:
            self._connect()
    
    def _connect(self):
        """Create SQL Server connection."""
        try:
            import pymssql
            
            SQLServerConnection._connection = pymssql.connect(
                server=SQLSERVER_CONFIG['server'],
                port=SQLSERVER_CONFIG['port'],
                user=SQLSERVER_CONFIG['user'],
                password=SQLSERVER_CONFIG['password'],
                database=SQLSERVER_CONFIG['database'],
                as_dict=True
            )
            print(f"✓ Connected to SQL Server: {SQLSERVER_CONFIG['database']}")
            
        except ImportError:
            print("ERROR: pymssql not installed. Run: pip install pymssql")
            raise
        except Exception as e:
            print(f"ERROR: SQL Server connection failed: {e}")
            raise
    
    @property
    def connection(self):
        """Get database connection."""
        if SQLServerConnection._connection is None:
            self._connect()
        return SQLServerConnection._connection
    
    def execute(self, query: str, params: tuple = None):
        """Execute a query with parameters."""
        cursor = self.connection.cursor(as_dict=True)
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor
    
    def execute_proc(self, proc_name: str, params: dict = None):
        """
        Execute a stored procedure.
        
        Args:
            proc_name: Name of stored procedure
            params: Dictionary of parameters
        """
        cursor = self.connection.cursor(as_dict=True)
        
        if params:
            # Build parameter string
            param_str = ', '.join([f"@{k}='{v}'" if isinstance(v, str) else f"@{k}={v}" 
                                   for k, v in params.items()])
            query = f"EXEC {proc_name} {param_str}"
        else:
            query = f"EXEC {proc_name}"
        
        cursor.execute(query)
        return cursor
    
    def fetch_one(self, query: str, params: tuple = None) -> dict:
        """Fetch single row as dictionary."""
        cursor = self.execute(query, params)
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def fetch_all(self, query: str, params: tuple = None) -> list:
        """Fetch all rows as list of dictionaries."""
        cursor = self.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows] if rows else []
    
    def commit(self):
        """Commit current transaction."""
        self.connection.commit()
    
    def rollback(self):
        """Rollback current transaction."""
        self.connection.rollback()
    
    def close(self):
        """Close database connection."""
        if SQLServerConnection._connection:
            SQLServerConnection._connection.close()
            SQLServerConnection._connection = None
    
    def get_table_count(self, table: str) -> int:
        """Get record count for a table."""
        result = self.fetch_one(f"SELECT COUNT(*) as count FROM {table}")
        return result['count'] if result else 0


class SQLiteConnection:
    """
    SQLite database connection manager.
    """
    
    _instance = None
    _connection = None
    
    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize connection."""
        if SQLiteConnection._connection is None:
            self._ensure_database_directory()
            self._connect()
            self._initialize_schema()
    
    def _ensure_database_directory(self):
        """Ensure database directory exists."""
        db_dir = os.path.dirname(DATABASE_PATH)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
    
    def _connect(self):
        """Create database connection."""
        import sqlite3
        SQLiteConnection._connection = sqlite3.connect(
            DATABASE_PATH,
            check_same_thread=False,
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
        SQLiteConnection._connection.row_factory = sqlite3.Row
        SQLiteConnection._connection.execute("PRAGMA foreign_keys = ON")
        print(f"✓ Connected to SQLite: {DATABASE_PATH}")
    
    def _initialize_schema(self):
        """Initialize database schema if not exists."""
        schema_path = os.path.join(os.path.dirname(DATABASE_PATH), 'schema.sql')
        if os.path.exists(schema_path):
            cursor = self._connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='USERS'"
            )
            if cursor.fetchone() is None:
                with open(schema_path, 'r') as f:
                    schema = f.read()
                SQLiteConnection._connection.executescript(schema)
                SQLiteConnection._connection.commit()
    
    @property
    def connection(self):
        """Get database connection."""
        if SQLiteConnection._connection is None:
            self._connect()
        return SQLiteConnection._connection
    
    def execute(self, query: str, params: tuple = None):
        """Execute a query with parameters."""
        cursor = self.connection.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor
    
    def execute_proc(self, proc_name: str, params: dict = None):
        """SQLite doesn't support stored procedures - stub method."""
        raise NotImplementedError("SQLite does not support stored procedures")
    
    def fetch_one(self, query: str, params: tuple = None) -> dict:
        """Fetch single row as dictionary."""
        cursor = self.execute(query, params)
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def fetch_all(self, query: str, params: tuple = None) -> list:
        """Fetch all rows as list of dictionaries."""
        cursor = self.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def commit(self):
        """Commit current transaction."""
        self.connection.commit()
    
    def rollback(self):
        """Rollback current transaction."""
        self.connection.rollback()
    
    def close(self):
        """Close database connection."""
        if SQLiteConnection._connection:
            SQLiteConnection._connection.close()
            SQLiteConnection._connection = None
    
    def get_table_count(self, table: str) -> int:
        """Get record count for a table."""
        result = self.fetch_one(f"SELECT COUNT(*) as count FROM {table}")
        return result['count'] if result else 0


# =================================================================
# DATABASE FACTORY
# =================================================================

# Global database instance
_db = None

def get_database():
    """
    Get or create global database connection.
    
    Uses DATABASE_TYPE to determine which backend to use:
    - 'sqlserver': Microsoft SQL Server (Docker)
    - 'sqlite': SQLite (local file)
    """
    global _db
    
    if _db is None:
        if DATABASE_TYPE == 'sqlserver':
            _db = SQLServerConnection()
        else:
            _db = SQLiteConnection()
    
    return _db


def get_database_type() -> str:
    """Get current database type."""
    return DATABASE_TYPE


def is_sqlserver() -> bool:
    """Check if using SQL Server."""
    return DATABASE_TYPE == 'sqlserver'


# For backwards compatibility
class DatabaseConnection:
    """Wrapper class for backwards compatibility."""
    
    def __new__(cls):
        return get_database()


# Test connection on import
if __name__ == "__main__":
    print(f"Database Type: {DATABASE_TYPE}")
    try:
        db = get_database()
        count = db.get_table_count('USERS')
        print(f"✓ Connection successful! Users count: {count}")
    except Exception as e:
        print(f"✗ Connection failed: {e}")
