"""
SRMS - Encryption Manager
AES-256 Encryption for sensitive data
"""

import os
import base64
import hashlib
import secrets
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import bcrypt


class EncryptionManager:
    """
    Manages AES-256 encryption for sensitive data and password hashing.
    
    Security Features:
    - AES-256 symmetric encryption for data at rest
    - bcrypt password hashing with salt
    - Secure key derivation using PBKDF2
    """
    
    def __init__(self, master_key: str = None):
        """
        Initialize encryption manager with master key.
        
        Args:
            master_key: Master encryption key (default: generates new key)
        """
        self.master_key = master_key or self._generate_master_key()
        self._key = self._derive_key(self.master_key)
        self._fernet = Fernet(self._key)
    
    def _generate_master_key(self) -> str:
        """Generate a secure master key."""
        return secrets.token_urlsafe(32)
    
    def _derive_key(self, password: str, salt: bytes = None) -> bytes:
        """
        Derive encryption key from password using PBKDF2.
        
        Args:
            password: Password or master key string
            salt: Optional salt bytes
        
        Returns:
            Base64-encoded derived key
        """
        if salt is None:
            salt = b'SRMS_SECURE_SALT_2024'  # In production, use unique salt per deployment
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt plaintext data using AES-256.
        
        Args:
            plaintext: String to encrypt
        
        Returns:
            Base64-encoded encrypted string
        """
        if plaintext is None:
            return None
        try:
            encrypted = self._fernet.encrypt(plaintext.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            raise EncryptionError(f"Encryption failed: {str(e)}")
    
    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt ciphertext data using AES-256.
        
        Args:
            ciphertext: Base64-encoded encrypted string
        
        Returns:
            Decrypted plaintext string
        """
        if ciphertext is None:
            return None
        try:
            encrypted = base64.urlsafe_b64decode(ciphertext.encode())
            decrypted = self._fernet.decrypt(encrypted)
            return decrypted.decode()
        except Exception as e:
            raise DecryptionError(f"Decryption failed: {str(e)}")
    
    @staticmethod
    def hash_password(password: str) -> tuple:
        """
        Hash password using bcrypt with salt.
        
        Args:
            password: Plain text password
        
        Returns:
            Tuple of (password_hash, salt)
        """
        salt = bcrypt.gensalt(rounds=12)
        password_hash = bcrypt.hashpw(password.encode(), salt)
        return password_hash.decode(), salt.decode()
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """
        Verify password against stored hash.
        
        Args:
            password: Plain text password to verify
            password_hash: Stored bcrypt hash
        
        Returns:
            True if password matches, False otherwise
        """
        try:
            return bcrypt.checkpw(password.encode(), password_hash.encode())
        except Exception:
            return False
    
    @staticmethod
    def generate_salt() -> str:
        """Generate a random salt for encryption."""
        return secrets.token_hex(16)
    
    def encrypt_column(self, value: any) -> str:
        """
        Encrypt a database column value.
        
        Args:
            value: Value to encrypt (converted to string)
        
        Returns:
            Encrypted string
        """
        return self.encrypt(str(value)) if value is not None else None
    
    def decrypt_column(self, encrypted_value: str) -> str:
        """
        Decrypt a database column value.
        
        Args:
            encrypted_value: Encrypted column value
        
        Returns:
            Decrypted string
        """
        return self.decrypt(encrypted_value) if encrypted_value else None


class EncryptionError(Exception):
    """Raised when encryption fails."""
    pass


class DecryptionError(Exception):
    """Raised when decryption fails."""
    pass


# Global encryption manager instance (initialized with environment key or default)
_encryption_manager = None

def get_encryption_manager() -> EncryptionManager:
    """Get or create the global encryption manager."""
    global _encryption_manager
    if _encryption_manager is None:
        # In production, get key from environment variable
        master_key = os.environ.get('SRMS_MASTER_KEY', 'SRMS_DEFAULT_SECURE_KEY_2024')
        _encryption_manager = EncryptionManager(master_key)
    return _encryption_manager
