"""Verification script for pool initialization locks.
This is a code review verification since the test environment lacks dependencies.
"""

def verify_pool_locks():
    """Verify pool initializers have lock guards."""
    print("POOL LOCKS VERIFICATION")
    print("=" * 60)
    print()
    
    # Read database.py
    with open("src/core/database.py", "r") as f:
        database_code = f.read()
    
    # Check for asyncio import
    if "import asyncio" in database_code:
        print("✓ asyncio imported")
    else:
        print("✗ asyncio not imported")
    
    # Check for threading import
    if "import threading" in database_code:
        print("✓ threading imported")
    else:
        print("✗ threading not imported")
    
    # Check for lock instances
    if "_postgres_lock = asyncio.Lock()" in database_code:
        print("✓ _postgres_lock defined as asyncio.Lock()")
    else:
        print("✗ _postgres_lock missing or incorrect type")
    
    if "_redis_lock = asyncio.Lock()" in database_code:
        print("✓ _redis_lock defined as asyncio.Lock()")
    else:
        print("✗ _redis_lock missing or incorrect type")
    
    if "_vault_lock = threading.Lock()" in database_code:
        print("✓ _vault_lock defined as threading.Lock()")
    else:
        print("✗ _vault_lock missing or incorrect type")
    
    # Check for lock usage in get_postgres_pool
    if "async with _postgres_lock:" in database_code:
        print("✓ get_postgres_pool uses _postgres_lock")
    else:
        print("✗ get_postgres_pool missing lock guard")
    
    # Check for lock usage in get_redis_pool
    if "async with _redis_lock:" in database_code:
        print("✓ get_redis_pool uses _redis_lock")
    else:
        print("✗ get_redis_pool missing lock guard")
    
    # Check for lock usage in get_vault_client
    if "with _vault_lock:" in database_code:
        print("✓ get_vault_client uses _vault_lock")
    else:
        print("✗ get_vault_client missing lock guard")
    
    # Check for double-checked locking pattern (if inside lock)
    if database_code.count("if _postgres_pool is None:") >= 2:
        print("✓ Double-checked locking pattern present")
    else:
        print("⚠ Double-checked locking not used (single check)")
    
    print()
    print("=" * 60)
    print("POOL LOCKS VERIFICATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    verify_pool_locks()
