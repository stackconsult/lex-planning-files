"""Proof Verification for LexRadar - cryptographic signature and Merkle proofs."""

from typing import Optional
from .proof_layer import ProofLayer, Proof
from .chain_anchor import ChainAnchor


class ProofVerifier:
    def __init__(self, proof_layer: ProofLayer, chain_anchor: ChainAnchor):
        self.proof_layer = proof_layer
        self.chain_anchor = chain_anchor

    def verify_proof_integrity(self, proof_id: str, content: str) -> bool:
        proof = self.proof_layer.get_proof(proof_id)
        if not proof:
            return False
        return self.proof_layer.verify_hash(content, proof.content_hash)

    def verify_chain_anchor(self, anchor_id: str, content_hash: str) -> bool:
        return self.chain_anchor.verify_anchor(anchor_id, content_hash)

    def verify_full_chain(self, proof_id: str, anchor_id: str, content: str) -> bool:
        proof = self.proof_layer.get_proof(proof_id)
        if not proof:
            return False

        if not self.proof_layer.verify_hash(content, proof.content_hash):
            return False

        return self.chain_anchor.verify_anchor(anchor_id, proof.content_hash)
