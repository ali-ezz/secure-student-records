"""
SRMS - SQL Server Authentication Module
Uses stored procedures for secure authentication
"""

import hashlib
from datetime import datetime
from typing import Optional, Dict, Any
from src.database.connection import get_database, is_sqlserver

# Define role clearance levels
ROLE_CLEARANCE = {
    'Admin': 4,
    'Instructor': 3,
    'TA': 2,
    'Student': 1,
    'Guest': 0
}


class SQLServerAuth:
    """
    SQL Server authentication using stored procedures and views.
    Falls back to SQLite-compatible queries when needed.
    """
    
    def __init__(self):
        self.db = get_database()
        self._use_sqlserver = is_sqlserver()
    
    def authenticate(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Authenticate user credentials.
        
        For SQL Server: Uses direct query since SP has OUTPUT params
        For SQLite: Uses regular query
        
        Returns user dict with role and clearance if authenticated.
        """
        if self._use_sqlserver:
            return self._authenticate_sqlserver(username, password)
        else:
            return self._authenticate_sqlite(username, password)
    
    def _authenticate_sqlserver(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """SQL Server authentication with password hashing."""
        try:
            # Get user record
            user = self.db.fetch_one(
                "SELECT UserID, Username, PasswordHash, PasswordSalt, Role, ClearanceLevel, "
                "IsActive, IsLocked, FailedLoginAttempts, LinkedID, LinkedType "
                "FROM USERS WHERE Username = %s",
                (username,)
            )
            
            if not user:
                return None
            
            # Check if account is locked or inactive
            if user.get('IsLocked', 0) == 1:
                return {'error': 'Account is locked. Contact administrator.'}
            
            if user.get('IsActive', 1) == 0:
                return {'error': 'Account is inactive.'}
            
            # Verify password using SHA2_256 (same as SQL Server)
            stored_hash = user.get('PasswordHash')
            stored_salt = user.get('PasswordSalt')
            
            if stored_hash and stored_salt:
                # Convert salt to string for hashing
                if isinstance(stored_salt, bytes):
                    salt_str = stored_salt.hex()
                else:
                    salt_str = str(stored_salt)
                
                # Compute hash same way as SQL Server
                computed_hash = hashlib.sha256(
                    (password + salt_str).encode('utf-8')
                ).digest()
                
                if computed_hash == stored_hash:
                    # Successful login - update last login
                    self.db.execute(
                        "UPDATE USERS SET LastLoginDate = GETDATE(), "
                        "FailedLoginAttempts = 0 WHERE UserID = %s",
                        (user['UserID'],)
                    )
                    self.db.commit()
                    
                    # Log successful login
                    self._log_action('LOGIN_SUCCESS', user['UserID'], username, user['Role'])
                    
                    return {
                        'user_id': user['UserID'],
                        'username': user['Username'],
                        'role': user['Role'],
                        'clearance_level': user['ClearanceLevel'],
                        'linked_id': user.get('LinkedID'),
                        'linked_type': user.get('LinkedType')
                    }
            
            # Failed login - increment counter
            failed_attempts = user.get('FailedLoginAttempts', 0) + 1
            
            if failed_attempts >= 5:
                self.db.execute(
                    "UPDATE USERS SET IsLocked = 1, FailedLoginAttempts = %s WHERE UserID = %s",
                    (failed_attempts, user['UserID'])
                )
                self.db.commit()
                return {'error': 'Account locked due to too many failed attempts.'}
            else:
                self.db.execute(
                    "UPDATE USERS SET FailedLoginAttempts = %s WHERE UserID = %s",
                    (failed_attempts, user['UserID'])
                )
                self.db.commit()
            
            self._log_action('LOGIN_FAILED', user['UserID'], username, user['Role'])
            return None
            
        except Exception as e:
            print(f"SQL Server auth error: {e}")
            return None
    
    def _authenticate_sqlite(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """SQLite fallback authentication."""
        from src.security.encryption import get_encryption_manager
        encryption = get_encryption_manager()
        
        user = self.db.fetch_one(
            "SELECT * FROM USERS WHERE username = ? AND is_active = 1",
            (username,)
        )
        
        if user and encryption.verify_password(password, user['password_hash']):
            return {
                'user_id': user['user_id'],
                'username': user['username'],
                'role': user['role'],
                'clearance_level': user['clearance_level'],
                'linked_id': user.get('linked_id'),
                'linked_type': user.get('linked_type')
            }
        return None
    
    def _log_action(self, action_type: str, user_id: int, username: str, role: str):
        """Log action to audit table."""
        try:
            if self._use_sqlserver:
                self.db.execute(
                    "INSERT INTO AUDIT_LOG (ActionType, UserID, Username, UserRole, "
                    "UserClearance, AccessGranted, ActionDate) "
                    "VALUES (%s, %s, %s, %s, %s, %s, GETDATE())",
                    (action_type, user_id, username, role, 
                     ROLE_CLEARANCE.get(role, 0), 1 if 'SUCCESS' in action_type else 0)
                )
                self.db.commit()
        except Exception as e:
            print(f"Audit log error: {e}")
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
        if self._use_sqlserver:
            return self.db.fetch_one(
                "SELECT UserID as user_id, Username as username, Role as role, "
                "ClearanceLevel as clearance_level, LinkedID as linked_id, "
                "LinkedType as linked_type FROM USERS WHERE UserID = %s",
                (user_id,)
            )
        else:
            return self.db.fetch_one(
                "SELECT * FROM USERS WHERE user_id = ?", (user_id,)
            )
    
    def get_all_users(self) -> list:
        """Get all users (Admin function)."""
        if self._use_sqlserver:
            return self.db.fetch_all(
                "SELECT UserID as user_id, Username as username, Role as role, "
                "ClearanceLevel as clearance_level, IsActive as is_active, "
                "LastLoginDate as last_login FROM USERS"
            )
        else:
            return self.db.fetch_all(
                "SELECT user_id, username, role, clearance_level, is_active, last_login FROM USERS"
            )


# Singleton instance
_auth = None

def get_auth() -> SQLServerAuth:
    """Get authentication manager instance."""
    global _auth
    if _auth is None:
        _auth = SQLServerAuth()
    return _auth


# Test
if __name__ == "__main__":
    auth = get_auth()
    print("Testing authentication...")
    
    # Test with known accounts
    test_accounts = [
        ('admin', 'admin123'),
        ('prof_smith', 'prof123'),
        ('student1', 'student123'),
    ]
    
    for username, password in test_accounts:
        result = auth.authenticate(username, password)
        if result and 'error' not in result:
            print(f"✓ {username}: Role={result['role']}, Clearance={result['clearance_level']}")
        else:
            print(f"✗ {username}: Failed - {result.get('error', 'Invalid credentials') if result else 'Invalid credentials'}")
