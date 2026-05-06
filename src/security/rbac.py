"""
SRMS - Role-Based Access Control (RBAC) Manager
Implements GRANT, REVOKE, DENY permissions
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from config import PERMISSION_MATRIX, ROLE_CLEARANCE, SecurityLevel


class RBACManager:
    """
    Role-Based Access Control Manager.
    
    Implements SQL-like GRANT, REVOKE, DENY permissions at application level.
    Each operation is verified against the permission matrix before execution.
    
    Security Features:
    - Role-based permission checking
    - Row-level security (own data vs all data)
    - Operation-level access control (SELECT, INSERT, UPDATE, DELETE)
    """
    
    def __init__(self):
        """Initialize RBAC Manager with permission matrix."""
        self.permission_matrix = PERMISSION_MATRIX.copy()
        self.role_clearance = ROLE_CLEARANCE.copy()
        self._denied_permissions = {}  # Explicit denials
    
    def get_role_clearance(self, role: str) -> int:
        """
        Get clearance level for a role.
        
        Args:
            role: User role name
        
        Returns:
            Clearance level (0-4)
        """
        return self.role_clearance.get(role, 0)
    
    def has_permission(self, role: str, table: str, operation: str, 
                       user_id: int = None, target_id: int = None) -> bool:
        """
        Check if role has permission for operation on table.
        
        Args:
            role: User role (Admin, Instructor, TA, Student, Guest)
            table: Table name
            operation: Operation type (SELECT, INSERT, UPDATE, DELETE)
            user_id: Current user's ID (for row-level checks)
            target_id: Target record's owner ID (for own-data checks)
        
        Returns:
            True if permission granted, False otherwise
        """
        # Check explicit denials first
        if self._is_denied(role, table, operation):
            return False
        
        # Get permissions for role and table
        role_perms = self.permission_matrix.get(role, {})
        table_perms = role_perms.get(table, [])
        
        # Check direct permission
        if operation in table_perms:
            return True
        
        # Check "own" permissions (e.g., SELECT_OWN)
        own_operation = f"{operation}_OWN"
        if own_operation in table_perms:
            # Only allow if accessing own data
            if user_id is not None and target_id is not None:
                return user_id == target_id
            return False
        
        # Check public permissions (for Guest)
        if f"{operation}_PUBLIC" in table_perms:
            return True
        
        return False
    
    def check_access(self, role: str, table: str, operation: str,
                     user_id: int = None, target_id: int = None) -> dict:
        """
        Check access and return detailed result.
        
        Args:
            role: User role
            table: Table name
            operation: Operation type
            user_id: Current user's ID
            target_id: Target record's owner ID
        
        Returns:
            Dictionary with access result and details
        """
        has_access = self.has_permission(role, table, operation, user_id, target_id)
        
        return {
            'granted': has_access,
            'role': role,
            'table': table,
            'operation': operation,
            'clearance': self.get_role_clearance(role),
            'reason': self._get_denial_reason(role, table, operation) if not has_access else 'Access granted'
        }
    
    def grant(self, role: str, table: str, operation: str):
        """
        Grant permission to a role for an operation on a table.
        Simulates SQL GRANT statement.
        
        Args:
            role: User role
            table: Table name
            operation: Operation to grant
        """
        if role not in self.permission_matrix:
            self.permission_matrix[role] = {}
        
        if table not in self.permission_matrix[role]:
            self.permission_matrix[role][table] = []
        
        if operation not in self.permission_matrix[role][table]:
            self.permission_matrix[role][table].append(operation)
        
        # Remove from denied if present
        self._remove_denial(role, table, operation)
    
    def revoke(self, role: str, table: str, operation: str):
        """
        Revoke permission from a role.
        Simulates SQL REVOKE statement.
        
        Args:
            role: User role
            table: Table name
            operation: Operation to revoke
        """
        if role in self.permission_matrix:
            if table in self.permission_matrix[role]:
                if operation in self.permission_matrix[role][table]:
                    self.permission_matrix[role][table].remove(operation)
    
    def deny(self, role: str, table: str, operation: str):
        """
        Explicitly deny permission to a role.
        Simulates SQL DENY statement.
        
        Args:
            role: User role
            table: Table name
            operation: Operation to deny
        """
        key = f"{role}:{table}:{operation}"
        self._denied_permissions[key] = True
    
    def _is_denied(self, role: str, table: str, operation: str) -> bool:
        """Check if operation is explicitly denied."""
        key = f"{role}:{table}:{operation}"
        return self._denied_permissions.get(key, False)
    
    def _remove_denial(self, role: str, table: str, operation: str):
        """Remove explicit denial."""
        key = f"{role}:{table}:{operation}"
        if key in self._denied_permissions:
            del self._denied_permissions[key]
    
    def _get_denial_reason(self, role: str, table: str, operation: str) -> str:
        """Get reason for denial."""
        if self._is_denied(role, table, operation):
            return f"Access explicitly DENIED for {role} to {operation} on {table}"
        
        if role not in self.permission_matrix:
            return f"Role '{role}' not recognized"
        
        if table not in self.permission_matrix[role]:
            return f"No permissions defined for {role} on {table}"
        
        return f"{operation} not granted to {role} on {table}"
    
    def get_role_permissions(self, role: str) -> dict:
        """
        Get all permissions for a role.
        
        Args:
            role: User role
        
        Returns:
            Dictionary of table -> permissions
        """
        return self.permission_matrix.get(role, {})
    
    def get_table_permissions(self, table: str) -> dict:
        """
        Get all role permissions for a table.
        
        Args:
            table: Table name
        
        Returns:
            Dictionary of role -> permissions
        """
        result = {}
        for role, tables in self.permission_matrix.items():
            if table in tables:
                result[role] = tables[table]
        return result
    
    def can_access_own_data_only(self, role: str, table: str, operation: str) -> bool:
        """
        Check if role can only access own data for this operation.
        
        Args:
            role: User role
            table: Table name
            operation: Operation type
        
        Returns:
            True if restricted to own data
        """
        role_perms = self.permission_matrix.get(role, {})
        table_perms = role_perms.get(table, [])
        
        # If has full access, not restricted
        if operation in table_perms:
            return False
        
        # If has OWN access, restricted to own data
        return f"{operation}_OWN" in table_perms


# Global RBAC manager instance
_rbac_manager = None

def get_rbac_manager() -> RBACManager:
    """Get or create the global RBAC manager."""
    global _rbac_manager
    if _rbac_manager is None:
        _rbac_manager = RBACManager()
    return _rbac_manager
