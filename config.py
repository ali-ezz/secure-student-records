"""
Secure Student Records Management System (SRMS)
Configuration and Security Level Definitions
"""

import os
from enum import IntEnum

# Database Configuration
DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'database', 'srms.db')

# Security Classification Levels (Bell-LaPadula)
class SecurityLevel(IntEnum):
    PUBLIC = 0           # Guest accessible
    UNCLASSIFIED = 1     # Basic course info
    CONFIDENTIAL = 2     # Student/Instructor profiles
    SECRET = 3           # Grades, Attendance
    TOP_SECRET = 4       # Disciplinary records

# User Roles with Clearance Levels
ROLE_CLEARANCE = {
    'Admin': SecurityLevel.TOP_SECRET,
    'Instructor': SecurityLevel.SECRET,
    'TA': SecurityLevel.CONFIDENTIAL,
    'Student': SecurityLevel.UNCLASSIFIED,
    'Guest': SecurityLevel.PUBLIC
}

# Data Classification
DATA_CLASSIFICATION = {
    'STUDENT': SecurityLevel.CONFIDENTIAL,
    'INSTRUCTOR': SecurityLevel.CONFIDENTIAL,
    'COURSE': SecurityLevel.UNCLASSIFIED,
    'COURSE_PUBLIC': SecurityLevel.PUBLIC,
    'GRADES': SecurityLevel.SECRET,
    'ATTENDANCE': SecurityLevel.SECRET,
    'USERS': SecurityLevel.TOP_SECRET
}

# RBAC Permission Matrix
# Format: {Role: {Table: [allowed_operations]}}
PERMISSION_MATRIX = {
    'Admin': {
        'STUDENT': ['SELECT', 'INSERT', 'UPDATE', 'DELETE'],
        'INSTRUCTOR': ['SELECT', 'INSERT', 'UPDATE', 'DELETE'],
        'COURSE': ['SELECT', 'INSERT', 'UPDATE', 'DELETE'],
        'GRADES': ['SELECT', 'INSERT', 'UPDATE', 'DELETE'],
        'ATTENDANCE': ['SELECT', 'INSERT', 'UPDATE', 'DELETE'],
        'USERS': ['SELECT', 'INSERT', 'UPDATE', 'DELETE'],
        'ROLE_REQUESTS': ['SELECT', 'INSERT', 'UPDATE', 'DELETE']
    },
    'Instructor': {
        'STUDENT': ['SELECT'],  # Assigned students only
        'INSTRUCTOR': ['SELECT_OWN', 'UPDATE_OWN'],
        'COURSE': ['SELECT'],
        'GRADES': ['SELECT', 'INSERT', 'UPDATE'],  # Assigned courses
        'ATTENDANCE': ['SELECT'],  # Assigned courses
        'USERS': [],
        'ROLE_REQUESTS': ['SELECT_OWN', 'INSERT']
    },
    'TA': {
        'STUDENT': ['SELECT'],  # Assigned students only
        'INSTRUCTOR': [],
        'COURSE': ['SELECT'],
        'GRADES': [],  # NO ACCESS
        'ATTENDANCE': ['SELECT', 'INSERT', 'UPDATE'],  # Assigned courses
        'USERS': [],
        'ROLE_REQUESTS': ['SELECT_OWN', 'INSERT']
    },
    'Student': {
        'STUDENT': ['SELECT_OWN'],
        'INSTRUCTOR': [],
        'COURSE': ['SELECT'],
        'GRADES': ['SELECT_OWN'],  # Only published
        'ATTENDANCE': ['SELECT_OWN'],
        'USERS': [],
        'ROLE_REQUESTS': ['SELECT_OWN', 'INSERT']
    },
    'Guest': {
        'STUDENT': [],
        'INSTRUCTOR': [],
        'COURSE': ['SELECT_PUBLIC'],
        'GRADES': [],
        'ATTENDANCE': [],
        'USERS': [],
        'ROLE_REQUESTS': []
    }
}

# Inference Control Settings
MIN_QUERY_SET_SIZE = 3  # Minimum records for aggregate queries

# Encryption Settings
ENCRYPTION_KEY_SIZE = 32  # AES-256
SALT_SIZE = 16

# Flow Control - Actions blocked for classified data
BLOCKED_ACTIONS = {
    SecurityLevel.TOP_SECRET: ['export', 'print', 'copy', 'paste', 'save', 'screenshot'],
    SecurityLevel.SECRET: ['export', 'print', 'copy', 'paste', 'save'],
    SecurityLevel.CONFIDENTIAL: ['export'],  # Restricted
    SecurityLevel.UNCLASSIFIED: [],
    SecurityLevel.PUBLIC: []
}

# GUI Theme Colors
THEME_COLORS = {
    'primary': '#1a73e8',
    'secondary': '#5f6368',
    'success': '#34a853',
    'danger': '#ea4335',
    'warning': '#fbbc04',
    'info': '#4285f4',
    'dark': '#202124',
    'light': '#f8f9fa',
    'bg_dark': '#1e1e2e',
    'bg_card': '#2d2d3f',
    'text': '#ffffff',
    'text_muted': '#a0a0a0'
}
