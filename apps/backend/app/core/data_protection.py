"""
Data encryption and protection utilities.

Provides encryption at rest, field-level encryption,
data anonymization, and secure data handling.
"""

import os
import base64
import hashlib
import secrets
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from enum import Enum
import json
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
import bcrypt

from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class EncryptionLevel(str, Enum):
    """Data encryption sensitivity levels."""
    PUBLIC = "public"          # No encryption needed
    INTERNAL = "internal"      # Basic encryption
    CONFIDENTIAL = "confidential"  # Strong encryption
    RESTRICTED = "restricted"  # Highest level encryption


class DataClassification(str, Enum):
    """Data classification for compliance."""
    PII = "pii"                # Personally Identifiable Information
    PHI = "phi"                # Protected Health Information
    FINANCIAL = "financial"    # Financial data
    TECHNICAL = "technical"    # Technical/Engineering data
    BUSINESS = "business"      # Business confidential
    PUBLIC = "public"          # Public information


class EncryptionManager:
    """
    Comprehensive encryption and data protection manager.
    """
    
    def __init__(self):
        self.master_key = self._get_or_create_master_key()
        self.fernet = Fernet(self.master_key)
        self.rsa_key_pair = self._get_or_create_rsa_keys()
    
    def _get_or_create_master_key(self) -> bytes:
        """Get or create the master encryption key."""
        # In production, this should come from a secure key management service
        key_env = os.getenv("VESSEL_GUARD_MASTER_KEY")
        
        if key_env:
            try:
                return base64.urlsafe_b64decode(key_env.encode())
            except Exception as e:
                logger.error(f"Invalid master key in environment: {e}")
        
        # For development/demo - generate a key
        # In production, this should be stored securely
        master_key = Fernet.generate_key()
        logger.warning("Generated new master key - store securely in production!")
        logger.info(f"Master key (store securely): {master_key.decode()}")
        return master_key
    
    def _get_or_create_rsa_keys(self) -> tuple:
        """Get or create RSA key pair for asymmetric encryption."""
        # For demo purposes, generate new keys
        # In production, load from secure storage
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        public_key = private_key.public_key()
        return private_key, public_key
    
    def encrypt_field(
        self,
        data: Union[str, int, float, dict, list],
        classification: DataClassification = DataClassification.BUSINESS
    ) -> str:
        """
        Encrypt a single field value.
        
        Args:
            data: Data to encrypt
            classification: Data classification level
            
        Returns:
            Base64 encoded encrypted data
        """
        try:
            # Convert to string if needed
            if isinstance(data, (dict, list)):
                data_str = json.dumps(data)
            else:
                data_str = str(data)
            
            # Add metadata
            metadata = {
                "classification": classification.value,
                "timestamp": datetime.utcnow().isoformat(),
                "version": "1.0"
            }
            
            payload = {
                "data": data_str,
                "metadata": metadata
            }
            
            # Encrypt using Fernet (symmetric encryption)
            encrypted_data = self.fernet.encrypt(json.dumps(payload).encode())
            
            # Return base64 encoded string for database storage
            return base64.urlsafe_b64encode(encrypted_data).decode()
            
        except Exception as e:
            logger.error(f"Failed to encrypt field: {e}")
            raise ValueError("Encryption failed")
    
    def decrypt_field(
        self,
        encrypted_data: str,
        expected_classification: Optional[DataClassification] = None
    ) -> Any:
        """
        Decrypt a field value.
        
        Args:
            encrypted_data: Base64 encoded encrypted data
            expected_classification: Expected data classification for validation
            
        Returns:
            Decrypted data in original format
        """
        try:
            # Decode from base64
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            
            # Decrypt using Fernet
            decrypted_bytes = self.fernet.decrypt(encrypted_bytes)
            payload = json.loads(decrypted_bytes.decode())
            
            # Validate classification if provided
            metadata = payload.get("metadata", {})
            if expected_classification:
                actual_classification = metadata.get("classification")
                if actual_classification != expected_classification.value:
                    logger.warning(f"Classification mismatch: expected {expected_classification}, got {actual_classification}")
            
            # Return original data
            data = payload["data"]
            
            # Try to parse as JSON (for dict/list)
            try:
                return json.loads(data)
            except (json.JSONDecodeError, TypeError):
                return data
                
        except Exception as e:
            logger.error(f"Failed to decrypt field: {e}")
            raise ValueError("Decryption failed")
    
    def encrypt_document(
        self,
        document: Dict[str, Any],
        field_classifications: Dict[str, DataClassification]
    ) -> Dict[str, Any]:
        """
        Encrypt specific fields in a document based on classification.
        
        Args:
            document: Document to encrypt
            field_classifications: Mapping of field names to classifications
            
        Returns:
            Document with encrypted fields
        """
        encrypted_doc = document.copy()
        
        for field_name, classification in field_classifications.items():
            if field_name in encrypted_doc:
                if classification != DataClassification.PUBLIC:
                    encrypted_doc[field_name] = self.encrypt_field(
                        encrypted_doc[field_name],
                        classification
                    )
                    # Mark field as encrypted
                    encrypted_doc[f"__{field_name}_encrypted"] = True
        
        return encrypted_doc
    
    def decrypt_document(
        self,
        encrypted_document: Dict[str, Any],
        field_classifications: Dict[str, DataClassification]
    ) -> Dict[str, Any]:
        """
        Decrypt specific fields in a document.
        
        Args:
            encrypted_document: Document with encrypted fields
            field_classifications: Mapping of field names to classifications
            
        Returns:
            Document with decrypted fields
        """
        decrypted_doc = encrypted_document.copy()
        
        for field_name, classification in field_classifications.items():
            if f"__{field_name}_encrypted" in decrypted_doc:
                if field_name in decrypted_doc:
                    decrypted_doc[field_name] = self.decrypt_field(
                        decrypted_doc[field_name],
                        classification
                    )
                # Remove encryption marker
                del decrypted_doc[f"__{field_name}_encrypted"]
        
        return decrypted_doc
    
    def hash_password(self, password: str) -> str:
        """
        Hash a password using bcrypt.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password
        """
        salt = bcrypt.gensalt(rounds=12)  # Strong hashing
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            password: Plain text password
            hashed_password: Stored hash
            
        Returns:
            True if password matches
        """
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    def generate_secure_token(self, length: int = 32) -> str:
        """Generate a cryptographically secure random token."""
        return secrets.token_urlsafe(length)
    
    def generate_api_key(self, user_id: int, organization_id: int) -> str:
        """Generate a secure API key."""
        random_part = secrets.token_urlsafe(24)
        timestamp = int(datetime.utcnow().timestamp())
        
        # Include user and org info for validation
        payload = f"{user_id}:{organization_id}:{timestamp}:{random_part}"
        
        # Hash to create final API key
        api_key_hash = hashlib.sha256(payload.encode()).hexdigest()
        
        # Format: vg_<first8chars>_<random16chars>
        return f"vg_{api_key_hash[:8]}_{secrets.token_urlsafe(12)}"


class DataAnonymizer:
    """
    Data anonymization and pseudonymization utilities.
    """
    
    def __init__(self, encryption_manager: EncryptionManager):
        self.encryption_manager = encryption_manager
    
    def anonymize_email(self, email: str) -> str:
        """Anonymize an email address."""
        if '@' not in email:
            return "***@***.***"
        
        local, domain = email.split('@', 1)
        
        # Keep first and last character of local part
        if len(local) <= 2:
            anonymized_local = "*" * len(local)
        else:
            anonymized_local = local[0] + "*" * (len(local) - 2) + local[-1]
        
        # Anonymize domain but keep structure
        domain_parts = domain.split('.')
        if len(domain_parts) >= 2:
            anonymized_domain = "*" * len(domain_parts[0]) + "." + domain_parts[-1]
        else:
            anonymized_domain = "*" * len(domain)
        
        return f"{anonymized_local}@{anonymized_domain}"
    
    def anonymize_phone(self, phone: str) -> str:
        """Anonymize a phone number."""
        # Remove all non-digits
        digits = ''.join(filter(str.isdigit, phone))
        
        if len(digits) < 4:
            return "*" * len(phone)
        
        # Show last 4 digits only
        return "*" * (len(digits) - 4) + digits[-4:]
    
    def anonymize_name(self, name: str) -> str:
        """Anonymize a person's name."""
        parts = name.split()
        
        anonymized_parts = []
        for part in parts:
            if len(part) <= 1:
                anonymized_parts.append("*")
            else:
                anonymized_parts.append(part[0] + "*" * (len(part) - 1))
        
        return " ".join(anonymized_parts)
    
    def anonymize_ip_address(self, ip: str) -> str:
        """Anonymize an IP address."""
        if '.' in ip:  # IPv4
            parts = ip.split('.')
            if len(parts) == 4:
                return f"{parts[0]}.{parts[1]}.XXX.XXX"
        elif ':' in ip:  # IPv6
            parts = ip.split(':')
            if len(parts) >= 4:
                return f"{parts[0]}:{parts[1]}:XXXX:XXXX:XXXX:XXXX:XXXX:XXXX"
        
        return "XXX.XXX.XXX.XXX"
    
    def pseudonymize_identifier(self, identifier: str, salt: str = None) -> str:
        """
        Create a consistent pseudonym for an identifier.
        
        Same input always produces same output with same salt.
        """
        if salt is None:
            salt = "vessel_guard_pseudonym"
        
        combined = f"{identifier}:{salt}"
        hash_obj = hashlib.sha256(combined.encode())
        return f"pseudo_{hash_obj.hexdigest()[:16]}"
    
    def anonymize_document(
        self,
        document: Dict[str, Any],
        anonymization_rules: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Anonymize fields in a document based on rules.
        
        Args:
            document: Document to anonymize
            anonymization_rules: Field name -> anonymization type mapping
                Types: email, phone, name, ip, pseudonym, remove
        """
        anonymized_doc = document.copy()
        
        for field_name, rule in anonymization_rules.items():
            if field_name in anonymized_doc:
                value = anonymized_doc[field_name]
                
                if rule == "email":
                    anonymized_doc[field_name] = self.anonymize_email(str(value))
                elif rule == "phone":
                    anonymized_doc[field_name] = self.anonymize_phone(str(value))
                elif rule == "name":
                    anonymized_doc[field_name] = self.anonymize_name(str(value))
                elif rule == "ip":
                    anonymized_doc[field_name] = self.anonymize_ip_address(str(value))
                elif rule == "pseudonym":
                    anonymized_doc[field_name] = self.pseudonymize_identifier(str(value))
                elif rule == "remove":
                    del anonymized_doc[field_name]
                elif rule == "hash":
                    hash_obj = hashlib.sha256(str(value).encode())
                    anonymized_doc[field_name] = hash_obj.hexdigest()[:16]
        
        return anonymized_doc


class SecureFileHandler:
    """
    Secure file handling with encryption and integrity checking.
    """
    
    def __init__(self, encryption_manager: EncryptionManager):
        self.encryption_manager = encryption_manager
    
    def encrypt_file(
        self,
        file_path: str,
        output_path: Optional[str] = None,
        classification: DataClassification = DataClassification.BUSINESS
    ) -> str:
        """
        Encrypt a file.
        
        Args:
            file_path: Path to file to encrypt
            output_path: Output path (optional)
            classification: Data classification
            
        Returns:
            Path to encrypted file
        """
        if output_path is None:
            output_path = file_path + ".encrypted"
        
        try:
            with open(file_path, 'rb') as infile:
                file_data = infile.read()
            
            # Create file metadata
            metadata = {
                "original_name": os.path.basename(file_path),
                "classification": classification.value,
                "encrypted_at": datetime.utcnow().isoformat(),
                "file_size": len(file_data),
                "checksum": hashlib.sha256(file_data).hexdigest()
            }
            
            # Combine metadata and file data
            payload = {
                "metadata": metadata,
                "data": base64.b64encode(file_data).decode()
            }
            
            # Encrypt the payload
            encrypted_data = self.encryption_manager.fernet.encrypt(
                json.dumps(payload).encode()
            )
            
            # Write encrypted file
            with open(output_path, 'wb') as outfile:
                outfile.write(encrypted_data)
            
            logger.info(f"Encrypted file {file_path} -> {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to encrypt file {file_path}: {e}")
            raise
    
    def decrypt_file(
        self,
        encrypted_file_path: str,
        output_path: Optional[str] = None,
        verify_checksum: bool = True
    ) -> str:
        """
        Decrypt a file.
        
        Args:
            encrypted_file_path: Path to encrypted file
            output_path: Output path (optional)
            verify_checksum: Whether to verify file integrity
            
        Returns:
            Path to decrypted file
        """
        try:
            with open(encrypted_file_path, 'rb') as infile:
                encrypted_data = infile.read()
            
            # Decrypt the payload
            decrypted_data = self.encryption_manager.fernet.decrypt(encrypted_data)
            payload = json.loads(decrypted_data.decode())
            
            # Extract metadata and file data
            metadata = payload["metadata"]
            file_data = base64.b64decode(payload["data"])
            
            # Verify checksum if requested
            if verify_checksum:
                actual_checksum = hashlib.sha256(file_data).hexdigest()
                expected_checksum = metadata["checksum"]
                if actual_checksum != expected_checksum:
                    raise ValueError("File integrity check failed")
            
            # Determine output path
            if output_path is None:
                original_name = metadata.get("original_name", "decrypted_file")
                output_path = os.path.join(
                    os.path.dirname(encrypted_file_path),
                    original_name
                )
            
            # Write decrypted file
            with open(output_path, 'wb') as outfile:
                outfile.write(file_data)
            
            logger.info(f"Decrypted file {encrypted_file_path} -> {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to decrypt file {encrypted_file_path}: {e}")
            raise


# Global instances for easy access
encryption_manager = EncryptionManager()
data_anonymizer = DataAnonymizer(encryption_manager)
secure_file_handler = SecureFileHandler(encryption_manager)


# Data classification schemas for common models
VESSEL_FIELD_CLASSIFICATIONS = {
    "name": DataClassification.BUSINESS,
    "registry_number": DataClassification.BUSINESS,
    "owner_name": DataClassification.PII,
    "owner_contact": DataClassification.PII,
    "technical_specifications": DataClassification.TECHNICAL,
    "inspection_history": DataClassification.TECHNICAL,
    "certification_data": DataClassification.BUSINESS
}

USER_FIELD_CLASSIFICATIONS = {
    "email": DataClassification.PII,
    "first_name": DataClassification.PII,
    "last_name": DataClassification.PII,
    "phone": DataClassification.PII,
    "address": DataClassification.PII,
    "emergency_contact": DataClassification.PII,
    "salary": DataClassification.FINANCIAL,
    "social_security": DataClassification.PII
}

CALCULATION_FIELD_CLASSIFICATIONS = {
    "input_parameters": DataClassification.TECHNICAL,
    "results": DataClassification.TECHNICAL,
    "material_properties": DataClassification.TECHNICAL,
    "safety_factors": DataClassification.TECHNICAL,
    "certification_data": DataClassification.BUSINESS
}

# Anonymization rules for data export/logging
AUDIT_ANONYMIZATION_RULES = {
    "email": "email",
    "phone": "phone",
    "first_name": "name", 
    "last_name": "name",
    "ip_address": "ip",
    "user_agent": "hash",
    "session_id": "pseudonym"
}
