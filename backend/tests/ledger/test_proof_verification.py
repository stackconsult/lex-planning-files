"""Tests for Proof Verification."""

import pytest
from src.ledger.proof_layer import ProofLayer
from src.ledger.chain_anchor import ChainAnchor
from src.ledger.proof_verification import ProofVerifier


class TestProofVerifier:
    def test_verify_proof_integrity_valid(self):
        proof_layer = ProofLayer()
        chain_anchor = ChainAnchor()
        verifier = ProofVerifier(proof_layer, chain_anchor)

        proof = proof_layer.create_proof("test content")
        assert verifier.verify_proof_integrity(proof.proof_id, "test content") is True

    def test_verify_proof_integrity_invalid_content(self):
        proof_layer = ProofLayer()
        chain_anchor = ChainAnchor()
        verifier = ProofVerifier(proof_layer, chain_anchor)

        proof = proof_layer.create_proof("test content")
        assert verifier.verify_proof_integrity(proof.proof_id, "wrong content") is False

    def test_verify_proof_integrity_nonexistent_proof(self):
        proof_layer = ProofLayer()
        chain_anchor = ChainAnchor()
        verifier = ProofVerifier(proof_layer, chain_anchor)

        assert verifier.verify_proof_integrity("nonexistent", "content") is False

    def test_verify_chain_anchor_valid(self):
        proof_layer = ProofLayer()
        chain_anchor = ChainAnchor()
        verifier = ProofVerifier(proof_layer, chain_anchor)

        anchor = chain_anchor.submit_anchor("hash123")
        assert verifier.verify_chain_anchor(anchor.anchor_id, "hash123") is True

    def test_verify_chain_anchor_invalid_hash(self):
        proof_layer = ProofLayer()
        chain_anchor = ChainAnchor()
        verifier = ProofVerifier(proof_layer, chain_anchor)

        anchor = chain_anchor.submit_anchor("hash123")
        assert verifier.verify_chain_anchor(anchor.anchor_id, "wrong") is False

    def test_verify_full_chain_valid(self):
        proof_layer = ProofLayer()
        chain_anchor = ChainAnchor()
        verifier = ProofVerifier(proof_layer, chain_anchor)

        proof = proof_layer.create_proof("test content")
        anchor = chain_anchor.submit_anchor(proof.content_hash)
        assert verifier.verify_full_chain(proof.proof_id, anchor.anchor_id, "test content") is True

    def test_verify_full_chain_invalid_content(self):
        proof_layer = ProofLayer()
        chain_anchor = ChainAnchor()
        verifier = ProofVerifier(proof_layer, chain_anchor)

        proof = proof_layer.create_proof("test content")
        anchor = chain_anchor.submit_anchor(proof.content_hash)
        assert verifier.verify_full_chain(proof.proof_id, anchor.anchor_id, "wrong") is False
