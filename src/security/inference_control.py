"""
SRMS - Inference Control Manager
Prevents deduction of sensitive data through statistical queries
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from config import MIN_QUERY_SET_SIZE


class InferenceController:
    """
    Inference Control Manager.
    
    Prevents information leakage through:
    - Query set size control (minimum records requirement)
    - Restricted aggregate functions
    - Tracker attack prevention
    - Statistical inference blocking
    
    Key Rules:
    - Minimum query set size: 3 records
    - Individual record identification blocked
    - Complementary query tracking
    """
    
    def __init__(self, min_set_size: int = None):
        """
        Initialize Inference Controller.
        
        Args:
            min_set_size: Minimum query set size (default: 3)
        """
        self.min_set_size = min_set_size or MIN_QUERY_SET_SIZE
        self._query_history = {}  # Track queries for tracker attack prevention
    
    def check_query_set_size(self, result_count: int) -> dict:
        """
        Check if query result set meets minimum size requirement.
        
        Args:
            result_count: Number of records in query result
        
        Returns:
            Dictionary with check result and details
        """
        is_allowed = result_count >= self.min_set_size or result_count == 0
        
        return {
            'allowed': is_allowed,
            'result_count': result_count,
            'min_required': self.min_set_size,
            'reason': self._get_size_reason(is_allowed, result_count)
        }
    
    def _get_size_reason(self, allowed: bool, count: int) -> str:
        """Get reason for query set size decision."""
        if allowed:
            if count == 0:
                return "No records found"
            return f"Query set size ({count}) meets minimum requirement ({self.min_set_size})"
        return f"BLOCKED: Query set size ({count}) below minimum ({self.min_set_size}) - Risk of individual identification"
    
    def validate_aggregate_query(self, query_type: str, result_count: int,
                                 user_role: str) -> dict:
        """
        Validate aggregate query against inference rules.
        
        Args:
            query_type: Type of aggregate (COUNT, AVG, SUM, MIN, MAX)
            result_count: Number of records in aggregate set
            user_role: Role of user making query
        
        Returns:
            Dictionary with validation result
        """
        # Check set size first
        size_check = self.check_query_set_size(result_count)
        if not size_check['allowed']:
            return {
                'allowed': False,
                'query_type': query_type,
                'reason': size_check['reason'],
                'risk': 'Individual identification through small aggregate set'
            }
        
        # Additional checks for sensitive aggregates
        sensitive_aggregates = ['MIN', 'MAX']
        if query_type.upper() in sensitive_aggregates:
            # MIN/MAX can reveal individual values
            if result_count < self.min_set_size * 2:  # Require larger set for MIN/MAX
                return {
                    'allowed': False,
                    'query_type': query_type,
                    'reason': f'{query_type} queries require at least {self.min_set_size * 2} records',
                    'risk': 'MIN/MAX can reveal individual extreme values'
                }
        
        return {
            'allowed': True,
            'query_type': query_type,
            'result_count': result_count,
            'reason': 'Aggregate query permitted'
        }
    
    def track_query(self, user_id: int, query_hash: str, result_set: set):
        """
        Track query for tracker attack prevention.
        
        Tracker attacks use complementary queries to deduce individual values.
        Example: Query A returns {1,2,3,4}, Query A' returns {1,2,4}
        → Individual 3's value can be deduced
        
        Args:
            user_id: User making the query
            query_hash: Hash of query structure
            result_set: Set of record IDs in result
        """
        if user_id not in self._query_history:
            self._query_history[user_id] = []
        
        self._query_history[user_id].append({
            'query_hash': query_hash,
            'result_set': result_set,
            'size': len(result_set)
        })
        
        # Keep only last 50 queries per user
        if len(self._query_history[user_id]) > 50:
            self._query_history[user_id] = self._query_history[user_id][-50:]
    
    def check_tracker_attack(self, user_id: int, new_result_set: set) -> dict:
        """
        Check for potential tracker attack pattern.
        
        Args:
            user_id: User making the query
            new_result_set: Result set of new query
        
        Returns:
            Dictionary with attack detection result
        """
        if user_id not in self._query_history:
            return {'attack_detected': False, 'risk_level': 'low'}
        
        history = self._query_history[user_id]
        
        for past_query in history:
            past_set = past_query['result_set']
            
            # Check for complementary query (difference of 1)
            diff = past_set.symmetric_difference(new_result_set)
            if len(diff) == 1:
                return {
                    'attack_detected': True,
                    'risk_level': 'high',
                    'reason': 'Potential tracker attack: Query pair can identify individual record',
                    'blocked': True
                }
            
            # Check for near-complementary queries
            if len(diff) <= self.min_set_size - 1 and len(diff) > 0:
                return {
                    'attack_detected': True,
                    'risk_level': 'medium',
                    'reason': f'Suspicious query pattern: Small difference ({len(diff)}) between query sets',
                    'blocked': False  # Warning only
                }
        
        return {'attack_detected': False, 'risk_level': 'low'}
    
    def create_restricted_view(self, base_columns: list, role: str) -> list:
        """
        Create a restricted column list based on role.
        
        Args:
            base_columns: Full list of columns
            role: User role
        
        Returns:
            Filtered list of columns accessible to role
        """
        # Define restricted columns per role
        restrictions = {
            'Student': ['password_hash', 'salt', 'clearance_level', 'security_classification'],
            'TA': ['password_hash', 'salt', 'grade_value', 'grade_value_encrypted', 'clearance_level'],
            'Guest': ['password_hash', 'salt', 'phone', 'phone_encrypted', 'email', 
                     'date_of_birth', 'grade_value', 'attendance', 'clearance_level',
                     'security_classification', 'student_id_encrypted']
        }
        
        restricted = restrictions.get(role, [])
        return [col for col in base_columns if col not in restricted]
    
    def anonymize_results(self, records: list, sensitive_fields: list) -> list:
        """
        Anonymize sensitive fields in query results.
        
        Args:
            records: List of record dictionaries
            sensitive_fields: Fields to anonymize
        
        Returns:
            Anonymized records
        """
        anonymized = []
        for record in records:
            anon_record = record.copy()
            for field in sensitive_fields:
                if field in anon_record:
                    anon_record[field] = '***REDACTED***'
            anonymized.append(anon_record)
        return anonymized
    
    def enforce_query_set_size(self, result_count: int) -> bool:
        """
        Enforce minimum query set size.
        
        Args:
            result_count: Number of records in result
        
        Returns:
            True if allowed
        
        Raises:
            InferenceControlError: If query set too small
        """
        check = self.check_query_set_size(result_count)
        if not check['allowed']:
            raise InferenceControlError(check['reason'])
        return True


class InferenceControlError(Exception):
    """Raised when inference control policy is violated."""
    pass


# Global inference controller instance
_inference_controller = None

def get_inference_controller() -> InferenceController:
    """Get or create the global inference controller."""
    global _inference_controller
    if _inference_controller is None:
        _inference_controller = InferenceController()
    return _inference_controller
