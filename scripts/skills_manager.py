#!/usr/bin/env python3
"""
Skills Manager — Domain-Agnostic Build Integration
Manages skills verification, installation, and reporting across all domains.

Usage:
    python3 scripts/skills_manager.py check      # Check required skills
    python3 scripts/skills_manager.py verify     # Verify skill levels
    python3 scripts/skills_manager.py install    # Install missing dependencies
    python3 scripts/skills_manager.py report     # Generate skills report
    python3 scripts/skills_manager.py get-domain # Get current domain
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional


class SkillsManager:
    """Domain-agnostic skills manager for build system integration."""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.manifest_path = self.project_root / ".github" / "skills" / "SKILLS_MANIFEST.json"
        self.manifest = self._load_manifest()

    def _load_manifest(self) -> Dict[str, Any]:
        """Load skills manifest from JSON file."""
        if not self.manifest_path.exists():
            print(f"ERROR: Skills manifest not found at {self.manifest_path}")
            sys.exit(1)
        
        with open(self.manifest_path, 'r') as f:
            return json.load(f)

    def get_domain(self) -> str:
        """Get current domain from manifest."""
        return self.manifest.get('domain', 'unknown')

    def check(self) -> bool:
        """Check required skills against manifest."""
        domain = self.get_domain()
        print(f"Checking skills for domain: {domain}")
        print(f"Skills Framework: {self.manifest.get('skills_framework', 'unknown')}")
        print(f"Manifest Version: {self.manifest.get('version', 'unknown')}")
        print()
        
        all_passed = True
        
        for category, category_data in self.manifest.get('skills', {}).items():
            print(f"=== {category_data.get('name', category)} ===")
            print(f"Required Level: {category_data.get('required_level', 'intermediate')}")
            print()
            
            # Check core technologies
            for tech in category_data.get('technologies', []):
                passed = self._check_technology(tech)
                if not passed:
                    all_passed = False
                print()
            
            # Check domain-specific technologies
            domain_specific = category_data.get('domain_specific', {}).get(domain, [])
            if domain_specific:
                print(f"--- Domain-Specific ({domain}) ---")
                for tech in domain_specific:
                    print(f"  ✓ {tech['name']}: {tech.get('description', 'No description')}")
                    print(f"    Level: {tech.get('level', 'intermediate')}")
                    print()
        
        return all_passed

    def _check_technology(self, tech: Dict[str, Any]) -> bool:
        """Check a single technology."""
        name = tech.get('name', 'unknown')
        version = tech.get('version', 'any')
        level = tech.get('level', 'intermediate')
        package = tech.get('package')
        verification_cmd = tech.get('verification_command')
        
        print(f"  {name} (>= {version})")
        print(f"    Required Level: {level}")
        
        if package:
            # Check if package is installed
            if self._is_package_installed(package):
                print(f"    Status: ✓ INSTALLED")
                return True
            else:
                print(f"    Status: ✗ NOT INSTALLED")
                return False
        elif verification_cmd:
            # Run verification command
            try:
                result = subprocess.run(
                    verification_cmd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    print(f"    Status: ✓ VERIFIED")
                    return True
                else:
                    print(f"    Status: ✗ NOT VERIFIED")
                    return False
            except Exception as e:
                print(f"    Status: ✗ ERROR: {e}")
                return False
        else:
            # Skill without package/verification (e.g., conceptual skill)
            print(f"    Status: ✓ CONCEPTUAL SKILL")
            return True

    def _is_package_installed(self, package: str) -> bool:
        """Check if a Python package is installed."""
        try:
            result = subprocess.run(
                ['pip', 'show', package],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except Exception:
            return False

    def verify(self) -> bool:
        """Verify skill levels and dependencies."""
        print("Verifying skill levels and dependencies...")
        print()
        return self.check()

    def install(self) -> bool:
        """Install missing skill dependencies."""
        print("Installing missing skill dependencies...")
        print()
        
        domain = self.get_domain()
        installed_count = 0
        failed_count = 0
        
        for category, category_data in self.manifest.get('skills', {}).items():
            for tech in category_data.get('technologies', []):
                package = tech.get('package')
                if package and not self._is_package_installed(package):
                    print(f"Installing {package}...")
                    try:
                        subprocess.run(
                            ['pip', 'install', package],
                            check=True,
                            timeout=300
                        )
                        print(f"  ✓ {package} installed successfully")
                        installed_count += 1
                    except Exception as e:
                        print(f"  ✗ Failed to install {package}: {e}")
                        failed_count += 1
            
            # Install domain-specific packages
            domain_specific = category_data.get('domain_specific', {}).get(domain, [])
            for tech in domain_specific:
                package = tech.get('package')
                if package and not self._is_package_installed(package):
                    print(f"Installing {package} (domain-specific)...")
                    try:
                        subprocess.run(
                            ['pip', 'install', package],
                            check=True,
                            timeout=300
                        )
                        print(f"  ✓ {package} installed successfully")
                        installed_count += 1
                    except Exception as e:
                        print(f"  ✗ Failed to install {package}: {e}")
                        failed_count += 1
        
        print()
        print(f"Installation complete: {installed_count} installed, {failed_count} failed")
        return failed_count == 0

    def report(self) -> None:
        """Generate skills report."""
        print("=" * 60)
        print("SKILLS REPORT")
        print("=" * 60)
        print()
        
        print(f"Domain: {self.get_domain()}")
        print(f"Skills Framework: {self.manifest.get('skills_framework', 'unknown')}")
        print(f"Manifest Version: {self.manifest.get('version', 'unknown')}")
        print(f"Last Updated: {self.manifest.get('last_updated', 'unknown')}")
        print()
        
        print("Skill Categories:")
        for category, category_data in self.manifest.get('skills', {}).items():
            print(f"  - {category_data.get('name', category)}")
            print(f"    Required Level: {category_data.get('required_level', 'intermediate')}")
            print(f"    Technologies: {len(category_data.get('technologies', []))}")
            
            domain = self.get_domain()
            domain_specific = category_data.get('domain_specific', {}).get(domain, [])
            if domain_specific:
                print(f"    Domain-Specific ({domain}): {len(domain_specific)}")
            print()
        
        print("=" * 60)
        print("EXTENSION PATTERN")
        print("=" * 60)
        print()
        print("To add a new domain:")
        print("1. Update 'domain' field in SKILLS_MANIFEST.json")
        print("2. Add domain-specific skills to each category")
        print("3. Run: make skills-check")
        print("4. Run: make skills-install")
        print()


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/skills_manager.py <command>")
        print("Commands: check, verify, install, report, get-domain")
        sys.exit(1)
    
    command = sys.argv[1]
    manager = SkillsManager()
    
    if command == 'check':
        success = manager.check()
        sys.exit(0 if success else 1)
    elif command == 'verify':
        success = manager.verify()
        sys.exit(0 if success else 1)
    elif command == 'install':
        success = manager.install()
        sys.exit(0 if success else 1)
    elif command == 'report':
        manager.report()
        sys.exit(0)
    elif command == 'get-domain':
        print(manager.get_domain())
        sys.exit(0)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == '__main__':
    main()
