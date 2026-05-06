"""
SRMS - Multilevel Security (MLS) Manager
Implements Bell-LaPadula Model (No Read Up, No Write Down)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from config import SecurityLevel, ROLE_CLEARANCE, DATA_CLASSIFICATION


class MLSManager:
    """
    Multilevel Security Manager implementing Bell-LaPadula Model.
    
    Security Principles:
    - No Read Up (NRU): Subject cannot read objects at higher classification
    - No Write Down (NWD): Subject cannot write to objects at lower classification (Bonus)
    
    Classification Levels:
    - Level 4: Top Secret (Admin only)
    - Level 3: Secret (Grades, Attendance)
    - Level 2: Confidential (Student/Instructor profiles)
    - Level 1: Unclassified (Course details)
    - Level 0: Public (Guest accessible)
    """
    
    def __init__(self, enforce_nwd: bool = True):
        """
        Initialize MLS Manager.
        
        Args:
            enforce_nwd: Whether to enforce No Write Down (bonus feature)
        """
        self.enforce_nwd = enforce_nwd
        self.role_clearance = ROLE_CLEARANCE.copy()
        self.data_classification = DATA_CLASSIFICATION.copy()
    
    def get_user_clearance(self, role: str) -> int:
        """
        Get clearance level for a user role.
        
        Args:
            role: User role name
        
        Returns:
            Clearance level (0-4)
        """
        return self.role_clearance.get(role, 0)
    
    def get_data_classification(self, table: str) -> int:
        """
        Get classification level for a data table.
        
        Args:
            table: Table name
        
        Returns:
            Classification level (0-4)
        """
        return self.data_classification.get(table, SecurityLevel.PUBLIC)
    
    def can_read(self, user_clearance: int, data_classification: int) -> bool:
        """
        Check if user can read data (No Read Up - NRU).
        
        Bell-LaPadula Simple Security Property:
        A subject can only read objects at or below their clearance level.
        
        Args:
            user_clearance: User's clearance level
            data_classification: Data's classification level
        
        Returns:
            True if read is allowed
        """
        # No Read Up: clearance >= classification
        return user_clearance >= data_classification
    
    def can_write(self, user_clearance: int, data_classification: int) -> bool:
        """
        Check if user can write data (No Write Down - NWD).
        
        Bell-LaPadula *-Property (Star Property):
        A subject can only write to objects at or above their clearance level.
        This prevents information leakage to lower classification levels.
        
        Args:
            user_clearance: User's clearance level
            data_classification: Data's classification level
        
        Returns:
            True if write is allowed
        """
        if not self.enforce_nwd:
            # If NWD not enforced, allow writing at or below clearance
            return user_clearance >= data_classification
        
        # No Write Down: can only write at same level or higher
        # Admin (4) can write anywhere, others restricted
        if user_clearance == SecurityLevel.TOP_SECRET:
            return True  # Admin can write anywhere
        
        return user_clearance <= data_classification
    
    def check_access(self, role: str, table: str, operation: str) -> dict:
        """
        Check MLS access for an operation.
        
        Args:
            role: User role
            table: Target table
            operation: 'read' or 'write'
        
        Returns:
            Dictionary with access result and details
        """
        user_clearance = self.get_user_clearance(role)
        data_classification = self.get_data_classification(table)
        
        if operation.lower() in ['select', 'read']:
            allowed = self.can_read(user_clearance, data_classification)
            rule = "No Read Up (NRU)"
        else:  # insert, update, delete = write
            allowed = self.can_write(user_clearance, data_classification)
            rule = "No Write Down (NWD)" if self.enforce_nwd else "Standard Write"
        
        return {
            'allowed': allowed,
            'role': role,
            'table': table,
            'operation': operation,
            'user_clearance': user_clearance,
            'user_clearance_name': SecurityLevel(user_clearance).name,
            'data_classification': data_classification,
            'data_classification_name': SecurityLevel(data_classification).name,
            'rule_applied': rule,
            'reason': self._get_access_reason(allowed, user_clearance, 
                                              data_classification, operation)
        }
    
    def _get_access_reason(self, allowed: bool, user_clearance: int,
                           data_classification: int, operation: str) -> str:
        """Get detailed reason for access decision."""
        if allowed:
            return f"Access granted: User clearance ({user_clearance}) permits {operation} on classification ({data_classification})"
        
        if operation.lower() in ['select', 'read']:
            return f"NRU Violation: Cannot read classification {data_classification} with clearance {user_clearance}"
        else:
            if self.enforce_nwd:
                return f"NWD Violation: Cannot write to classification {data_classification} with clearance {user_clearance}"
            else:
                return f"Access denied: Insufficient clearance for {operation}"
    
    def get_accessible_tables(self, role: str, operation: str = 'read') -> list:
        """
        Get list of tables accessible by role.
        
        Args:
            role: User role
            operation: 'read' or 'write'
        
        Returns:
            List of accessible table names
        """
        user_clearance = self.get_user_clearance(role)
        accessible = []
        
        for table, classification in self.data_classification.items():
            if operation.lower() in ['select', 'read']:
                if self.can_read(user_clearance, classification):
                    accessible.append(table)
            else:
                if self.can_write(user_clearance, classification):
                    accessible.append(table)
        
        return accessible
    
    def get_classification_label(self, level: int) -> str:
        """
        Get human-readable label for classification level.
        
        Args:
            level: Classification level (0-4)
        
        Returns:
            Classification name string
        """
        labels = {
            0: "PUBLIC",
            1: "UNCLASSIFIED",
            2: "CONFIDENTIAL",
            3: "SECRET",
            4: "TOP SECRET"
        }
        return labels.get(level, "UNKNOWN")
    
    def filter_records_by_clearance(self, records: list, clearance: int,
                                    classification_field: str = 'security_classification') -> list:
        """
        Filter records based on user clearance (NRU enforcement).
        
        Args:
            records: List of record dictionaries
            clearance: User's clearance level
            classification_field: Field name containing classification
        
        Returns:
            Filtered list of records user can access
        """
        return [
            record for record in records
            if self.can_read(clearance, record.get(classification_field, 0))
        ]
    
    def enforce_read_access(self, role: str, table: str) -> bool:
        """
        Enforce read access based on MLS.
        
        Args:
            role: User role
            table: Target table
        
        Returns:
            True if access allowed
        
        Raises:
            MLSViolationError: If access violates MLS policy
        """
        result = self.check_access(role, table, 'read')
        if not result['allowed']:
            raise MLSViolationError(result['reason'])
        return True
    
    def enforce_write_access(self, role: str, table: str) -> bool:
        """
        Enforce write access based on MLS.
        
        Args:
            role: User role
            table: Target table
        
        Returns:
            True if access allowed
        
        Raises:
            MLSViolationError: If access violates MLS policy
        """
        result = self.check_access(role, table, 'write')
        if not result['allowed']:
            raise MLSViolationError(result['reason'])
        return True


class MLSViolationError(Exception):
    """Raised when MLS policy is violated."""
    pass


# Global MLS manager instance
_mls_manager = None

def get_mls_manager(enforce_nwd: bool = True) -> MLSManager:
    """Get or create the global MLS manager."""
    global _mls_manager
    if _mls_manager is None:
        _mls_manager = MLSManager(enforce_nwd=enforce_nwd)
    return _mls_manager
