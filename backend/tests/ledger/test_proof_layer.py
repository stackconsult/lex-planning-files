"""Tests for Immutable Proof Layer."""

import pytest
from datetime import datetime
from src.ledger.proof_layer import ProofLayer, Proof


class TestProofLayer:
    """Test immutable proof layer functionality."""

    def test_generate_hash_creates_sha256(self):
        """Verify SHA-256 hash generation."""
        layer = ProofLayer()
        content = "test content"
        hash_result = layer.generate_hash(content)

        # SHA-256 produces 64-character hex string
        assert len(hash_result) == 64
        assert all(c in "0123456789abcdef" for c in hash_result)

    def test_generate_hash_deterministic(self):
        """Verify hash is deterministic for same content."""
        layer = ProofLayer()
        content = "test content"
        hash1 = layer.generate_hash(content)
        hash2 = layer.generate_hash(content)

        assert hash1 == hash2

    def test_generate_hash_different_for_different_content(self):
        """Verify hash differs for different content."""
        layer = ProofLayer()
        hash1 = layer.generate_hash("content1")
        hash2 = layer.generate_hash("content2")

        assert hash1 != hash2

    def test_generate_hash_rejects_empty_content(self):
        """Verify empty content raises error."""
        layer = ProofLayer()

        with pytest.raises(ValueError, match="Content cannot be empty"):
            layer.generate_hash("")

    def test_create_proof_stores_hash_not_content(self):
        """Verify proof stores hash, not content (IP-G1 guardrail)."""
        layer = ProofLayer()
        content = "sensitive IP content"
        proof = layer.create_proof(content)

        # Proof contains hash, not content
        assert proof.content_hash == layer.generate_hash(content)
        assert "sensitive IP content" not in str(proof)
        assert len(proof.content_hash) == 64

    def test_create_proof_generates_unique_id(self):
        """Verify each proof gets unique ID."""
        layer = ProofLayer()
        proof1 = layer.create_proof("content1")
        proof2 = layer.create_proof("content2")

        assert proof1.proof_id != proof2.proof_id

    def test_create_proof_includes_timestamp(self):
        """Verify proof includes timestamp."""
        layer = ProofLayer()
        proof = layer.create_proof("content")

        assert isinstance(proof.timestamp, datetime)
        assert proof.timestamp <= datetime.utcnow()

    def test_get_proof_retrieves_stored_proof(self):
        """Verify proof retrieval by ID."""
        layer = ProofLayer()
        proof = layer.create_proof("content")
        retrieved = layer.get_proof(proof.proof_id)

        assert retrieved is not None
        assert retrieved.proof_id == proof.proof_id
        assert retrieved.content_hash == proof.content_hash

    def test_get_proof_returns_none_for_nonexistent(self):
        """Verify None returned for nonexistent proof."""
        layer = ProofLayer()
        retrieved = layer.get_proof("nonexistent")

        assert retrieved is None

    def test_verify_hash_matches_correct_content(self):
        """Verify hash verification for correct content."""
        layer = ProofLayer()
        content = "test content"
        expected_hash = layer.generate_hash(content)

        assert layer.verify_hash(content, expected_hash) is True

    def test_verify_hash_rejects_incorrect_content(self):
        """Verify hash verification rejects incorrect content."""
        layer = ProofLayer()
        hash1 = layer.generate_hash("content1")
        hash2 = layer.generate_hash("content2")

        assert layer.verify_hash("content1", hash2) is False

    def test_verify_proof_valid_for_correct_content(self):
        """Verify proof validation for correct content."""
        layer = ProofLayer()
        content = "test content"
        proof = layer.create_proof(content)

        assert layer.verify_proof(proof.proof_id, content) is True

    def test_verify_proof_invalid_for_incorrect_content(self):
        """Verify proof validation rejects incorrect content."""
        layer = ProofLayer()
        proof = layer.create_proof("content1")

        assert layer.verify_proof(proof.proof_id, "content2") is False

    def test_verify_proof_invalid_for_nonexistent_proof(self):
        """Verify proof validation rejects nonexistent proof."""
        layer = ProofLayer()

        assert layer.verify_proof("nonexistent", "content") is False

    def test_guardrail_ip_g1_only_hash_on_chain(self):
        """Verify IP-G1 guardrail: only hash stored, never content."""
        layer = ProofLayer()
        sensitive_content = "This is sensitive IP that must never be stored on-chain"
        proof = layer.create_proof(sensitive_content)

        # Verify only hash is stored
        assert sensitive_content not in str(proof)
        assert proof.content_hash == layer.generate_hash(sensitive_content)
        assert len(proof.content_hash) == 64  # SHA-256 hex length

        # Verify content can be reconstructed from hash (for verification)
        assert layer.verify_proof(proof.proof_id, sensitive_content)
