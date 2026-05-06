"""
SRMS - Database Switcher
Allows switching between SQLite and SQL Server
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Database configuration
DATABASE_CONFIG = {
    'type': 'sqlite',  # Options: 'sqlite', 'sqlserver'
    
    # SQLite settings
    'sqlite': {
        'path': os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                            'database', 'srms.db')
    },
    
    # SQL Server settings
    'sqlserver': {
        'server': 'localhost',
        'database': 'SRMS_SecureDB',
        'username': 'SA',
        'password': 'YourPassword123!',
        'driver': 'ODBC Driver 18 for SQL Server',
        'trusted_connection': False,
        'trust_certificate': True
    }
}


def get_connection():
    """
    Get database connection based on configuration.
    
    Returns:
        Database connection object
    """
    db_type = DATABASE_CONFIG.get('type', 'sqlite')
    
    if db_type == 'sqlite':
        return get_sqlite_connection()
    elif db_type == 'sqlserver':
        return get_sqlserver_connection()
    else:
        raise ValueError(f"Unknown database type: {db_type}")


def get_sqlite_connection():
    """Get SQLite connection."""
    import sqlite3
    
    db_path = DATABASE_CONFIG['sqlite']['path']
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    return conn


def get_sqlserver_connection():
    """Get SQL Server connection."""
    config = DATABASE_CONFIG['sqlserver']
    
    try:
        import pyodbc
        
        if config.get('trusted_connection'):
            conn_str = (
                f"DRIVER={{{config['driver']}}};"
                f"SERVER={config['server']};"
                f"DATABASE={config['database']};"
                f"Trusted_Connection=yes;"
            )
        else:
            conn_str = (
                f"DRIVER={{{config['driver']}}};"
                f"SERVER={config['server']};"
                f"DATABASE={config['database']};"
                f"UID={config['username']};"
                f"PWD={config['password']};"
            )
        
        if config.get('trust_certificate'):
            conn_str += "TrustServerCertificate=yes;"
        
        conn = pyodbc.connect(conn_str)
        return conn
        
    except ImportError:
        print("pyodbc not installed. Install with: pip install pyodbc")
        raise
    except Exception as e:
        print(f"SQL Server connection error: {e}")
        raise


def set_database_type(db_type: str):
    """
    Set the database type.
    
    Args:
        db_type: 'sqlite' or 'sqlserver'
    """
    if db_type not in ['sqlite', 'sqlserver']:
        raise ValueError("db_type must be 'sqlite' or 'sqlserver'")
    
    DATABASE_CONFIG['type'] = db_type
    print(f"Database type set to: {db_type}")


def get_database_type() -> str:
    """Get current database type."""
    return DATABASE_CONFIG.get('type', 'sqlite')


def configure_sqlserver(server: str, database: str, username: str, password: str):
    """
    Configure SQL Server connection.
    
    Args:
        server: SQL Server hostname
        database: Database name
        username: SQL Server username
        password: SQL Server password
    """
    DATABASE_CONFIG['sqlserver'].update({
        'server': server,
        'database': database,
        'username': username,
        'password': password
    })
    print(f"SQL Server configured: {server}/{database}")


def test_connection() -> bool:
    """
    Test current database connection.
    
    Returns:
        True if connection successful
    """
    try:
        conn = get_connection()
        
        if DATABASE_CONFIG['type'] == 'sqlite':
            cursor = conn.execute("SELECT 1")
        else:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
        
        conn.close()
        print(f"✅ {DATABASE_CONFIG['type'].upper()} connection successful!")
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False


# Export convenience function
def use_sqlite():
    """Switch to SQLite database."""
    set_database_type('sqlite')


def use_sqlserver():
    """Switch to SQL Server database."""
    set_database_type('sqlserver')


if __name__ == "__main__":
    # Test connections
    print("Testing SQLite connection...")
    use_sqlite()
    test_connection()
    
    print("\nTo use SQL Server, configure and test:")
    print("  configure_sqlserver('localhost', 'SRMS_SecureDB', 'SA', 'YourPass123!')")
    print("  use_sqlserver()")
    print("  test_connection()")
