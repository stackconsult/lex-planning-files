"""Verification script for RLS tenant injection with parameterized query.
This is a code review verification since the test environment lacks dependencies.
"""

def verify_rls_injection_code():
    """Verify RLS tenant injection uses parameterized query."""
    print("RLS TENANT INJECTION VERIFICATION")
    print("=" * 60)
    print()
    
    # Read db_session.py
    with open("src/core/db_session.py", "r") as f:
        db_session_code = f.read()
    
    # Check for parameterized query
    if 'text("SET LOCAL app.tenant_id = :tenant_id")' in db_session_code:
        print("✓ RLS injection uses parameterized query with text()")
    else:
        print("✗ RLS injection missing parameterized query")
    
    # Check for bind parameters
    if '{"tenant_id": str(tenant_id)}' in db_session_code:
        print("✓ RLS injection uses bind parameters")
    else:
        print("✗ RLS injection missing bind parameters")
    
    # Check for SQL import
    if "from sqlalchemy import text" in db_session_code:
        print("✓ SQLAlchemy text() imported")
    else:
        print("✗ SQLAlchemy text() not imported")
    
    # Check for old f-string approach (should NOT be present)
    if 'f"SET LOCAL app.tenant_id' in db_session_code:
        print("✗ OLD: F-string still present (SQL injection vulnerability)")
    else:
        print("✓ F-string approach removed")
    
    print()
    print("=" * 60)
    print("RLS INJECTION VERIFICATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    verify_rls_injection_code()
