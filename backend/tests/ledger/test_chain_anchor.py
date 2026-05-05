"""Tests for Chain Anchoring."""

import pytest
from datetime import datetime
from src.ledger.chain_anchor import ChainAnchor, Anchor


class TestChainAnchor:
    def test_submit_anchor(self):
        anchorer = ChainAnchor()
        anchor = anchorer.submit_anchor("hash123")
        assert anchor.content_hash == "hash123"
        assert anchor.tx_hash.startswith("0x")
        assert isinstance(anchor.timestamp, datetime)

    def test_get_anchor(self):
        anchorer = ChainAnchor()
        anchor = anchorer.submit_anchor("hash123")
        retrieved = anchorer.get_anchor(anchor.anchor_id)
        assert retrieved is not None
        assert retrieved.anchor_id == anchor.anchor_id

    def test_verify_anchor_valid(self):
        anchorer = ChainAnchor()
        anchor = anchorer.submit_anchor("hash123")
        assert anchorer.verify_anchor(anchor.anchor_id, "hash123") is True

    def test_verify_anchor_invalid_hash(self):
        anchorer = ChainAnchor()
        anchor = anchorer.submit_anchor("hash123")
        assert anchorer.verify_anchor(anchor.anchor_id, "wrong") is False

    def test_verify_anchor_nonexistent(self):
        anchorer = ChainAnchor()
        assert anchorer.verify_anchor("nonexistent", "hash") is False
