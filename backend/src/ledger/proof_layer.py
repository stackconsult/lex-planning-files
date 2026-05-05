"""Immutable Proof Layer for LexRadar.

This module provides SHA-256 hashing for IP content to ensure only hashes
are stored on-chain, never raw IP content (IP-G1 guardrail).
"""

import hashlib
from typing import Dict, Optional
from datetime import datetime
from dataclasses import dataclass


@dataclass
class Proof:
    """Immutable proof record."""
    proof_id: str
    content_hash: str
    timestamp: datetime
    metadata: Dict[str, str]


class ProofLayer:
    """Immutable proof layer for IP content hashing."""

    def __init__(self):
        """Initialize proof layer."""
        self._proofs: Dict[str, Proof] = {}

    def generate_hash(self, content: str) -> str:
        """Generate SHA-256 hash of content.

        Args:
            content: IP content to hash

        Returns:
            SHA-256 hash as hex string

        Guardrail: IP-G1 - Only SHA-256 hash on-chain, never IP content
        """
        if not content:
            raise ValueError("Content cannot be empty")

        # SHA-256 hashing
        hash_obj = hashlib.sha256(content.encode('utf-8'))
        return hash_obj.hexdigest()

    def create_proof(self, content: str, metadata: Optional[Dict[str, str]] = None) -> Proof:
        """Create immutable proof for content.

        Args:
            content: IP content to prove
            metadata: Optional metadata

        Returns:
            Proof record with hash (not content)

        Guardrail: IP-G1 - Only SHA-256 hash on-chain, never IP content
        """
        content_hash = self.generate_hash(content)
        proof_id = hashlib.sha256(f"{content_hash}{datetime.utcnow().isoformat()}".encode()).hexdigest()

        proof = Proof(
            proof_id=proof_id,
            content_hash=content_hash,
            timestamp=datetime.utcnow(),
            metadata=metadata or {}
        )

        self._proofs[proof_id] = proof
        return proof

    def get_proof(self, proof_id: str) -> Optional[Proof]:
        """Retrieve proof by ID.

        Args:
            proof_id: Proof identifier

        Returns:
            Proof record or None if not found
        """
        return self._proofs.get(proof_id)

    def verify_hash(self, content: str, expected_hash: str) -> bool:
        """Verify content matches expected hash.

        Args:
            content: Content to verify
            expected_hash: Expected SHA-256 hash

        Returns:
            True if hash matches, False otherwise
        """
        actual_hash = self.generate_hash(content)
        return actual_hash == expected_hash

    def verify_proof(self, proof_id: str, content: str) -> bool:
        """Verify proof matches content.

        Args:
            proof_id: Proof identifier
            content: Content to verify

        Returns:
            True if proof is valid, False otherwise
        """
        proof = self.get_proof(proof_id)
        if not proof:
            return False

        return self.verify_hash(content, proof.content_hash)
