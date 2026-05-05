"""BYOK Implementation - tenant-specific encryption keys."""

import hashlib
import secrets
from typing import Dict, Optional
from datetime import datetime
from dataclasses import dataclass


@dataclass
class TenantKey:
    tenant_id: str
    key_id: str
    encrypted_key: str
    key_version: int
    created_at: datetime
    rotated_at: Optional[datetime] = None
    revoked_at: Optional[datetime] = None


class BYOKManager:
    def __init__(self):
        self._keys: Dict[str, TenantKey] = {}
        self._key_history: Dict[str, list] = {}

    def generate_key_id(self) -> str:
        return secrets.token_hex(16)

    def derive_key(self, tenant_id: str, key_id: str) -> str:
        combined = f"{tenant_id}:{key_id}".encode('utf-8')
        return hashlib.sha256(combined).hexdigest()

    def encrypt_key(self, plaintext_key: str, master_key: str) -> str:
        encrypted = []
        for p, m in zip(plaintext_key, master_key):
            encrypted.append(chr(ord(p) ^ ord(m)))
        return ''.join(encrypted).encode('utf-8').hex()

    def create_tenant_key(self, tenant_id: str, master_key: str) -> TenantKey:
        key_id = self.generate_key_id()
        plaintext_key = self.derive_key(tenant_id, key_id)
        encrypted_key = self.encrypt_key(plaintext_key, master_key)

        key = TenantKey(
            tenant_id=tenant_id,
            key_id=key_id,
            encrypted_key=encrypted_key,
            key_version=1,
            created_at=datetime.utcnow()
        )

        self._keys[tenant_id] = key
        self._key_history[tenant_id] = [key]
        return key

    def rotate_key(self, tenant_id: str, master_key: str) -> TenantKey:
        old_key = self._keys.get(tenant_id)
        if not old_key:
            raise ValueError(f"No key for tenant {tenant_id}")

        key_id = self.generate_key_id()
        plaintext_key = self.derive_key(tenant_id, key_id)
        encrypted_key = self.encrypt_key(plaintext_key, master_key)

        new_key = TenantKey(
            tenant_id=tenant_id,
            key_id=key_id,
            encrypted_key=encrypted_key,
            key_version=old_key.key_version + 1,
            created_at=datetime.utcnow(),
            rotated_at=datetime.utcnow()
        )

        self._keys[tenant_id] = new_key
        self._key_history[tenant_id].append(new_key)
        return new_key

    def revoke_key(self, tenant_id: str) -> None:
        key = self._keys.get(tenant_id)
        if key:
            key.revoked_at = datetime.utcnow()

    def get_key(self, tenant_id: str) -> Optional[TenantKey]:
        return self._keys.get(tenant_id)

    def is_key_revoked(self, tenant_id: str) -> bool:
        key = self._keys.get(tenant_id)
        return key is not None and key.revoked_at is not None
