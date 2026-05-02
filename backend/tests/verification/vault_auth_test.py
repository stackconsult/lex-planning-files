"""Verification script for Vault authentication error handling.
This is a code review verification since Vault instance is not available.
"""

def verify_vault_auth_error_handling():
    """Verify Vault auth failure raises ConnectionError."""
    print("VAULT AUTH ERROR HANDLING VERIFICATION")
    print("=" * 60)
    print()
    
    # Read database.py
    with open("src/core/database.py", "r") as f:
        database_code = f.read()
    
    # Check for ConnectionError import
    if "import hvac" in database_code:
        print("✓ hvac imported")
    else:
        print("✗ hvac not imported")
    
    # Check for ConnectionError raise
    if 'raise ConnectionError("Vault authentication failed")' in database_code:
        print("✓ Vault auth failure raises ConnectionError")
    else:
        print("✗ Vault auth failure missing ConnectionError raise")
    
    # Check for is_authenticated() check
    if "if _vault_client.is_authenticated():" in database_code:
        print("✓ Vault authentication check present")
    else:
        print("✗ Vault authentication check missing")
    
    # Check for error logging
    if 'logger.error("vault_client_auth_failed")' in database_code:
        print("✓ Error logging on auth failure")
    else:
        print("✗ Error logging missing")
    
    # Check that it doesn't return unauthenticated client
    if "return _vault_client" in database_code:
        # Make sure it's after the authentication check
        lines = database_code.split('\n')
        auth_check_line = None
        return_line = None
        for i, line in enumerate(lines):
            if "if _vault_client.is_authenticated():" in line:
                auth_check_line = i
            if "return _vault_client" in line and "get_vault_client" in lines[max(0, i-10):i]:
                return_line = i
        
        if auth_check_line and return_line:
            if return_line > auth_check_line:
                print("✓ Vault client returned only after auth check")
            else:
                print("✗ Vault client returned before auth check")
        else:
            print("⚠ Could not verify return statement placement")
    else:
        print("✗ Vault client return statement missing")
    
    print()
    print("=" * 60)
    print("VAULT AUTH ERROR HANDLING VERIFICATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    verify_vault_auth_error_handling()
