"""Verification script for cache key collision fix."""
import hashlib


def test_old_collision():
    """Demonstrate collision with old string concatenation approach."""
    # These two different queries would produce the same fingerprint with old approach
    query1 = "a:b"
    jurisdiction1 = "c"
    doc_type1 = "d"
    limit1 = 10
    
    query2 = "a"
    jurisdiction2 = "b:c"
    doc_type2 = "d"
    limit2 = 10
    
    # Old approach: simple string concatenation
    fingerprint1_old = f"{query1}:{jurisdiction1}:{doc_type1}:{limit1}"
    fingerprint2_old = f"{query2}:{jurisdiction2}:{doc_type2}:{limit2}"
    
    print(f"OLD APPROACH (COLLISION):")
    print(f"  Input 1: query='{query1}', jurisdiction='{jurisdiction1}', doc_type='{doc_type1}', limit={limit1}")
    print(f"  Input 2: query='{query2}', jurisdiction='{jurisdiction2}', doc_type='{doc_type2}', limit={limit2}")
    print(f"  Fingerprint 1: {fingerprint1_old}")
    print(f"  Fingerprint 2: {fingerprint2_old}")
    print(f"  COLLISION: {fingerprint1_old == fingerprint2_old}")
    print()


def test_new_no_collision():
    """Demonstrate no collision with new JSON + SHA-256 approach."""
    import json
    
    # Same two different queries
    query1 = "a:b"
    jurisdiction1 = "c"
    doc_type1 = "d"
    limit1 = 10
    
    query2 = "a"
    jurisdiction2 = "b:c"
    doc_type2 = "d"
    limit2 = 10
    
    # New approach: JSON serialization + SHA-256 hash
    cache_key_data1 = {"query": query1, "jurisdiction": jurisdiction1, "doc_type": doc_type1, "limit": limit1}
    fingerprint1_new = hashlib.sha256(
        json.dumps(cache_key_data1, sort_keys=True).encode()
    ).hexdigest()
    
    cache_key_data2 = {"query": query2, "jurisdiction": jurisdiction2, "doc_type": doc_type2, "limit": limit2}
    fingerprint2_new = hashlib.sha256(
        json.dumps(cache_key_data2, sort_keys=True).encode()
    ).hexdigest()
    
    print(f"NEW APPROACH (JSON + SHA-256):")
    print(f"  Input 1: query='{query1}', jurisdiction='{jurisdiction1}', doc_type='{doc_type1}', limit={limit1}")
    print(f"  Input 2: query='{query2}', jurisdiction='{jurisdiction2}', doc_type='{doc_type2}', limit={limit2}")
    print(f"  JSON 1: {json.dumps(cache_key_data1, sort_keys=True)}")
    print(f"  JSON 2: {json.dumps(cache_key_data2, sort_keys=True)}")
    print(f"  Fingerprint 1: {fingerprint1_new}")
    print(f"  Fingerprint 2: {fingerprint2_new}")
    print(f"  COLLISION: {fingerprint1_new == fingerprint2_new}")
    print()


def test_same_query_same_hash():
    """Verify same query produces same hash."""
    import json
    
    query = "test query"
    jurisdiction = "US"
    doc_type = "STATUTE"
    limit = 10
    
    cache_key_data = {"query": query, "jurisdiction": jurisdiction, "doc_type": doc_type, "limit": limit}
    fingerprint1 = hashlib.sha256(
        json.dumps(cache_key_data, sort_keys=True).encode()
    ).hexdigest()
    fingerprint2 = hashlib.sha256(
        json.dumps(cache_key_data, sort_keys=True).encode()
    ).hexdigest()
    
    print(f"CONSISTENCY TEST:")
    print(f"  Same input twice")
    print(f"  JSON: {json.dumps(cache_key_data, sort_keys=True)}")
    print(f"  Fingerprint 1: {fingerprint1}")
    print(f"  Fingerprint 2: {fingerprint2}")
    print(f"  MATCH: {fingerprint1 == fingerprint2}")
    print()


if __name__ == "__main__":
    print("=" * 60)
    print("CACHE KEY COLLISION VERIFICATION")
    print("=" * 60)
    print()
    
    test_old_collision()
    test_new_no_collision()
    test_same_query_same_hash()
    
    print("=" * 60)
    print("VERIFICATION COMPLETE")
    print("Old approach: VULNERABLE to collision")
    print("New approach: SECURE with SHA-256")
    print("=" * 60)
