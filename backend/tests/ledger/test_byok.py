"""Tests for BYOK Implementation."""

import pytest
from datetime import datetime
from src.ledger.byok import BYOKManager, TenantKey


class TestBYOKManager:
    def test_generate_key_id_unique(self):
        manager = BYOKManager()
        id1 = manager.generate_key_id()
        id2 = manager.generate_key_id()
        assert id1 != id2
        assert len(id1) == 32

    def test_derive_key_deterministic(self):
        manager = BYOKManager()
        key1 = manager.derive_key("tenant1", "key1")
        key2 = manager.derive_key("tenant1", "key1")
        assert key1 == key2

    def test_derive_key_different_for_different_inputs(self):
        manager = BYOKManager()
        key1 = manager.derive_key("tenant1", "key1")
        key2 = manager.derive_key("tenant2", "key1")
        assert key1 != key2

    def test_create_tenant_key(self):
        manager = BYOKManager()
        key = manager.create_tenant_key("tenant1", "master123")
        assert key.tenant_id == "tenant1"
        assert key.key_version == 1
        assert key.encrypted_key is not None
        assert isinstance(key.created_at, datetime)

    def test_create_tenant_key_stores_encrypted_not_plaintext(self):
        manager = BYOKManager()
        key = manager.create_tenant_key("tenant1", "master123")
        plaintext = manager.derive_key("tenant1", key.key_id)
        assert plaintext not in key.encrypted_key

    def test_rotate_key_increments_version(self):
        manager = BYOKManager()
        manager.create_tenant_key("tenant1", "master123")
        rotated = manager.rotate_key("tenant1", "master123")
        assert rotated.key_version == 2

    def test_rotate_key_creates_audit_trail(self):
        manager = BYOKManager()
        manager.create_tenant_key("tenant1", "master123")
        manager.rotate_key("tenant1", "master123")
        history = manager._key_history["tenant1"]
        assert len(history) == 2

    def test_revoke_key_sets_revoked_at(self):
        manager = BYOKManager()
        manager.create_tenant_key("tenant1", "master123")
        manager.revoke_key("tenant1")
        key = manager.get_key("tenant1")
        assert key.revoked_at is not None

    def test_is_key_revoked_true_after_revoke(self):
        manager = BYOKManager()
        manager.create_tenant_key("tenant1", "master123")
        manager.revoke_key("tenant1")
        assert manager.is_key_revoked("tenant1") is True

    def test_is_key_revoked_false_for_active_key(self):
        manager = BYOKManager()
        manager.create_tenant_key("tenant1", "master123")
        assert manager.is_key_revoked("tenant1") is False

    def test_get_key_returns_none_for_nonexistent(self):
        manager = BYOKManager()
        assert manager.get_key("nonexistent") is None
