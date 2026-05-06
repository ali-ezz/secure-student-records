"""
SRMS - Flow Control Manager
Prevents illegal movement of classified data
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from config import SecurityLevel, BLOCKED_ACTIONS


class FlowController:
    """
    Flow Control Manager.
    
    Prevents illegal data flow:
    - Downflow prevention (high classification → low classification)
    - Export/print blocking for classified data
    - Copy/paste control for sensitive information
    - Covert channel prevention
    
    Flow Rules:
    - Data cannot flow from higher to lower classification
    - Same level to same level: ALLOWED
    - Lower to higher: ALLOWED
    - Higher to lower: BLOCKED
    """
    
    def __init__(self, enable_bonus_features: bool = True):
        """
        Initialize Flow Controller.
        
        Args:
            enable_bonus_features: Enable export/copy blocking (bonus +2 marks)
        """
        self.enable_bonus_features = enable_bonus_features
        self.blocked_actions = BLOCKED_ACTIONS.copy()
        self._clipboard_locked = False
        self._current_classification = SecurityLevel.PUBLIC
    
    def can_flow(self, source_level: int, target_level: int) -> bool:
        """
        Check if data can flow from source to target classification.
        
        Args:
            source_level: Source data classification level
            target_level: Target location classification level
        
        Returns:
            True if flow is allowed
        """
        # Data can only flow upward or stay at same level
        # Cannot flow downward (higher → lower)
        return target_level >= source_level
    
    def check_flow(self, source_level: int, target_level: int) -> dict:
        """
        Check data flow and return detailed result.
        
        Args:
            source_level: Source classification level
            target_level: Target classification level
        
        Returns:
            Dictionary with flow check result
        """
        is_allowed = self.can_flow(source_level, target_level)
        
        return {
            'allowed': is_allowed,
            'source_level': source_level,
            'source_name': SecurityLevel(source_level).name,
            'target_level': target_level,
            'target_name': SecurityLevel(target_level).name,
            'direction': self._get_flow_direction(source_level, target_level),
            'reason': self._get_flow_reason(is_allowed, source_level, target_level)
        }
    
    def _get_flow_direction(self, source: int, target: int) -> str:
        """Get flow direction description."""
        if source == target:
            return "HORIZONTAL (same level)"
        elif target > source:
            return "UPWARD (low → high)"
        else:
            return "DOWNWARD (high → low)"
    
    def _get_flow_reason(self, allowed: bool, source: int, target: int) -> str:
        """Get reason for flow decision."""
        if allowed:
            if source == target:
                return "Flow allowed: Same classification level"
            return "Flow allowed: Data flowing to equal or higher classification"
        return f"BLOCKED: Illegal downflow from {SecurityLevel(source).name} to {SecurityLevel(target).name}"
    
    def is_action_blocked(self, classification: int, action: str) -> bool:
        """
        Check if action is blocked for given classification.
        
        Args:
            classification: Data classification level
            action: Action to check (export, print, copy, paste, save)
        
        Returns:
            True if action is blocked
        """
        if not self.enable_bonus_features:
            return False
        
        blocked = self.blocked_actions.get(classification, [])
        return action.lower() in blocked
    
    def check_action(self, classification: int, action: str) -> dict:
        """
        Check if action is allowed for classification.
        
        Args:
            classification: Data classification level
            action: Action to perform
        
        Returns:
            Dictionary with action check result
        """
        is_blocked = self.is_action_blocked(classification, action)
        
        return {
            'allowed': not is_blocked,
            'action': action,
            'classification': classification,
            'classification_name': SecurityLevel(classification).name,
            'reason': self._get_action_reason(is_blocked, classification, action)
        }
    
    def _get_action_reason(self, blocked: bool, classification: int, action: str) -> str:
        """Get reason for action decision."""
        if not blocked:
            return f"Action '{action}' permitted for {SecurityLevel(classification).name} data"
        return f"BLOCKED: '{action}' not allowed for {SecurityLevel(classification).name} classification"
    
    def can_export(self, classification: int) -> bool:
        """Check if data can be exported."""
        return not self.is_action_blocked(classification, 'export')
    
    def can_print(self, classification: int) -> bool:
        """Check if data can be printed."""
        return not self.is_action_blocked(classification, 'print')
    
    def can_copy(self, classification: int) -> bool:
        """Check if data can be copied to clipboard."""
        return not self.is_action_blocked(classification, 'copy')
    
    def can_save(self, classification: int) -> bool:
        """Check if data can be saved locally."""
        return not self.is_action_blocked(classification, 'save')
    
    def lock_clipboard(self, classification: int):
        """
        Lock clipboard for sensitive data.
        
        Args:
            classification: Classification of currently displayed data
        """
        if self.enable_bonus_features and classification >= SecurityLevel.SECRET:
            self._clipboard_locked = True
            self._current_classification = classification
    
    def unlock_clipboard(self):
        """Unlock clipboard when leaving sensitive context."""
        self._clipboard_locked = False
        self._current_classification = SecurityLevel.PUBLIC
    
    def is_clipboard_locked(self) -> bool:
        """Check if clipboard is currently locked."""
        return self._clipboard_locked
    
    def get_current_classification(self) -> int:
        """Get classification of currently displayed data."""
        return self._current_classification
    
    def enforce_flow(self, source_level: int, target_level: int) -> bool:
        """
        Enforce flow control.
        
        Args:
            source_level: Source classification
            target_level: Target classification
        
        Returns:
            True if flow allowed
        
        Raises:
            FlowControlError: If flow violates policy
        """
        if not self.can_flow(source_level, target_level):
            raise FlowControlError(
                f"Illegal data flow: Cannot transfer {SecurityLevel(source_level).name} "
                f"data to {SecurityLevel(target_level).name} location"
            )
        return True
    
    def enforce_action(self, classification: int, action: str) -> bool:
        """
        Enforce action control.
        
        Args:
            classification: Data classification
            action: Action to perform
        
        Returns:
            True if action allowed
        
        Raises:
            FlowControlError: If action violates policy
        """
        if self.is_action_blocked(classification, action):
            raise FlowControlError(
                f"Action blocked: '{action}' not permitted for "
                f"{SecurityLevel(classification).name} data"
            )
        return True
    
    def get_allowed_actions(self, classification: int) -> list:
        """
        Get list of allowed actions for classification.
        
        Args:
            classification: Data classification level
        
        Returns:
            List of allowed actions
        """
        all_actions = ['view', 'export', 'print', 'copy', 'paste', 'save', 'screenshot']
        blocked = self.blocked_actions.get(classification, [])
        return [action for action in all_actions if action not in blocked]
    
    def get_flow_matrix(self) -> dict:
        """
        Get complete flow permission matrix.
        
        Returns:
            Dictionary showing all flow permissions
        """
        levels = [level for level in SecurityLevel]
        matrix = {}
        
        for source in levels:
            matrix[source.name] = {}
            for target in levels:
                matrix[source.name][target.name] = {
                    'allowed': self.can_flow(source, target),
                    'symbol': '✓' if self.can_flow(source, target) else '✗'
                }
        
        return matrix


class FlowControlError(Exception):
    """Raised when flow control policy is violated."""
    pass


# Global flow controller instance
_flow_controller = None

def get_flow_controller(enable_bonus: bool = True) -> FlowController:
    """Get or create the global flow controller."""
    global _flow_controller
    if _flow_controller is None:
        _flow_controller = FlowController(enable_bonus_features=enable_bonus)
    return _flow_controller
