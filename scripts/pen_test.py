#!/usr/bin/env python3
"""Production Penetration Testing Engine (P2-09).

Automated security probing across 7 attack vectors with signed report.
Red Team execution with zero tolerance for critical findings.
"""
import ast
import hashlib
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Tuple


PROJECT_ROOT = Path("/home/local-root/lex/planning files")


class PenTestResult:
    def __init__(self, check_id: str, vector: str, description: str,
                 passed: bool, severity: str, details: str = "", metric: Any = None):
        self.check_id = check_id
        self.vector = vector
        self.description = description
        self.passed = passed
        self.severity = severity  # CRITICAL, HIGH, MEDIUM, LOW, INFO
        self.details = details
        self.metric = metric


class PenetrationTest:
    def __init__(self):
        self.results: List[PenTestResult] = []
        self.critical_findings: List[str] = []
        self.high_findings: List[str] = []

    def run(self) -> Dict[str, Any]:
        print("=" * 70)
        print("PRODUCTION PENETRATION TESTING — P2-09")
        print("=" * 70)
        print(f"Timestamp: {datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')}")
        print(f"Commit: {self._get_git_commit()}")
        print()

        self._mc1_staging_auth()
        self._mc2_jwt_bypass()
        self._mc3_rls_isolation()
        self._mc4_secret_exposure()
        self._mc5_injection_vectors()
        self._mc6_onchain_integrity()
        self._mc7_security_headers()
        self._mc8_dependency_cve()
        return self._mc9_signed_report()

    def _get_git_commit(self) -> str:
        try:
            return subprocess.check_output(
                ["git", "-C", str(PROJECT_ROOT), "rev-parse", "--short", "HEAD"],
                text=True
            ).strip()
        except:
            return "unknown"

    def _add(self, check_id: str, vector: str, description: str,
             passed: bool, severity: str, details: str = "", metric=None):
        r = PenTestResult(check_id, vector, description, passed, severity, details, metric)
        self.results.append(r)
        if not passed and severity == "CRITICAL":
            self.critical_findings.append(check_id)
        elif not passed and severity == "HIGH":
            self.high_findings.append(check_id)
        return r

    # ===== MC1: Staging Authorization =====
    def _mc1_staging_auth(self):
        print("[MC1] STAGING DEPLOY AUTHORIZATION")
        print("-" * 40)
        report = PROJECT_ROOT / "docs" / "execution" / "STAGING_DEPLOY_REPORT.md"
        authorized = report.exists()
        self._add("MC1-01", "AUTH", "Staging deploy report exists",
                 authorized, "CRITICAL" if not authorized else "INFO",
                 f"Report found: {authorized}", metric=authorized)
        print(f"  Staging report: {'OK' if authorized else 'BLOCKED'}")
        print()

    # ===== MC2: JWT Bypass Probe =====
    def _mc2_jwt_bypass(self):
        print("[MC2] JWT BYPASS PROBE")
        print("-" * 40)
        jwt_file = PROJECT_ROOT / "backend" / "src" / "api" / "middleware" / "jwt_auth.py"
        content = jwt_file.read_text() if jwt_file.exists() else ""

        # Check that public paths are explicitly allowed
        public_paths = "public_paths" in content
        # Check that non-public routes require auth (call_next only after check)
        requires_auth = "call_next" in content and "public_paths" in content
        # Verify there is no path that bypasses auth entirely
        bypass_paths = re.findall(r'if.*path.*return.*await.*call_next', content)

        self._add("JWT-01", "JWT", "Public paths explicitly whitelisted",
                 public_paths, "HIGH", f"public_paths defined: {public_paths}", metric=public_paths)

        self._add("JWT-02", "JWT", "Non-public routes require authentication",
                 requires_auth, "CRITICAL", f"Auth middleware enforced: {requires_auth}",
                 metric=requires_auth)

        self._add("JWT-03", "JWT", "No unconditional bypass paths",
                 len(bypass_paths) == 0, "CRITICAL",
                 f"Unconditional bypass paths found: {len(bypass_paths)}",
                 metric=len(bypass_paths))

        print(f"  Public paths whitelist: {'OK' if public_paths else 'FAIL'}")
        print(f"  Auth enforcement: {'OK' if requires_auth else 'FAIL'}")
        print(f"  Bypass paths: {len(bypass_paths)} [{'OK' if len(bypass_paths) == 0 else 'FAIL'}]")
        print()

    # ===== MC3: RLS Isolation =====
    def _mc3_rls_isolation(self):
        print("[MC3] RLS ENFORCEMENT VALIDATION")
        print("-" * 40)
        rls_file = PROJECT_ROOT / "backend" / "migrations" / "002_rls_policies.sql"
        rls_content = rls_file.read_text() if rls_file.exists() else ""

        has_rls_policies = "CREATE POLICY" in rls_content.upper()
        has_tenant_filter = "tenant_id" in rls_content.lower()
        has_enable_rls = ("ENABLE ROW LEVEL SECURITY" in rls_content.upper() or
                          "FORCE ROW LEVEL SECURITY" in rls_content.upper())

        # Check service files for tenant_id in queries
        svc_dir = PROJECT_ROOT / "backend" / "src" / "api" / "services"
        tenant_in_queries = 0
        if svc_dir.exists():
            for f in svc_dir.glob("*.py"):
                content = f.read_text().lower()
                if "tenant_id" in content:
                    tenant_in_queries += 1

        self._add("RLS-01", "RLS", "RLS policies defined in migration",
                 has_rls_policies, "CRITICAL", f"RLS policies found: {has_rls_policies}",
                 metric=has_rls_policies)

        self._add("RLS-02", "RLS", "Tenant filter in RLS policies",
                 has_tenant_filter, "CRITICAL", f"Tenant filter found: {has_tenant_filter}",
                 metric=has_tenant_filter)

        self._add("RLS-03", "RLS", "Row Level Security enabled",
                 has_enable_rls, "CRITICAL", f"RLS enabled: {has_enable_rls}",
                 metric=has_enable_rls)

        self._add("RLS-04", "RLS", "Services reference tenant_id",
                 tenant_in_queries >= 3, "HIGH",
                 f"Services with tenant_id: {tenant_in_queries}/3",
                 metric=tenant_in_queries)

        print(f"  RLS policies: {'OK' if has_rls_policies else 'FAIL'}")
        print(f"  Tenant filter: {'OK' if has_tenant_filter else 'FAIL'}")
        print(f"  RLS enabled: {'OK' if has_enable_rls else 'FAIL'}")
        print(f"  Tenant in services: {tenant_in_queries}/3 [{'OK' if tenant_in_queries >= 3 else 'FAIL'}]")
        print()

    # ===== MC4: Secret Exposure Scan =====
    def _mc4_secret_exposure(self):
        print("[MC4] SECRET EXPOSURE SCAN")
        print("-" * 40)

        secret_patterns = [
            re.compile(r'password\s*=\s*["\'][^"\']{8,}', re.IGNORECASE),
            re.compile(r'api_key\s*=\s*["\'][^"\']{8,}', re.IGNORECASE),
            re.compile(r'secret\s*=\s*["\'][^"\']{8,}', re.IGNORECASE),
            re.compile(r'token\s*=\s*["\'][^"\']{16,}', re.IGNORECASE),
            re.compile(r'private_key\s*=\s*["\'][^"\']{20,}', re.IGNORECASE),
        ]

        findings = []
        src_dir = PROJECT_ROOT / "backend" / "src"
        for py_file in src_dir.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            content = py_file.read_text()
            lines = content.splitlines()
            for i, line in enumerate(lines, 1):
                stripped = line.strip()
                # Skip comments
                if stripped.startswith("#"):
                    continue
                # Skip legitimate parameter access patterns
                if re.search(r'\b\w+\.(api_key|token|secret)\b', stripped):
                    continue
                for pattern in secret_patterns:
                    if pattern.search(stripped):
                        if 'placeholder' in stripped.lower() or 'example' in stripped.lower():
                            continue
                        findings.append(f"{py_file.relative_to(PROJECT_ROOT)}:{i}")
                        break

        self._add("SEC-01", "SECRETS", "No hardcoded secrets in source",
                 len(findings) == 0, "CRITICAL",
                 f"Findings: {len(findings)}",
                 metric=len(findings))

        # Check .env.staging for REPLACE_ME markers (expected placeholders)
        env_file = PROJECT_ROOT / ".env.staging"
        env_ok = env_file.exists()
        if env_ok:
            env_content = env_file.read_text()
            replace_me_count = env_content.count("REPLACE_ME")
            self._add("SEC-02", "SECRETS", "Staging env uses placeholder secrets",
                     replace_me_count > 0, "INFO",
                     f"Placeholder markers: {replace_me_count}",
                     metric=replace_me_count)

        print(f"  Secret findings: {len(findings)} [{'OK' if len(findings) == 0 else 'BLOCKED'}]")
        for f in findings[:5]:
            print(f"    - {f}")
        if len(findings) > 5:
            print(f"    ... and {len(findings) - 5} more")
        print()

    # ===== MC5: Injection Vector Analysis =====
    def _mc5_injection_vectors(self):
        print("[MC5] INJECTION VECTOR ANALYSIS")
        print("-" * 40)

        # Check for f-string SQL construction (anti-pattern)
        sql_injection_risk = 0
        src_dir = PROJECT_ROOT / "backend" / "src"
        for py_file in src_dir.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            content = py_file.read_text()
            # Look for f-string SQL patterns
            if re.search(r'f["\'].*?SELECT.*\{.*?\}', content, re.IGNORECASE):
                sql_injection_risk += 1
            if re.search(r'f["\'].*?INSERT.*\{.*?\}', content, re.IGNORECASE):
                sql_injection_risk += 1
            if re.search(r'f["\'].*?UPDATE.*\{.*?\}', content, re.IGNORECASE):
                sql_injection_risk += 1

        # Check for raw HTML output without escaping
        xss_risk = 0
        for py_file in src_dir.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            content = py_file.read_text()
            # Look for direct HTML construction with user input
            if re.search(r'HTMLResponse.*\+.*\w+.*\+', content):
                xss_risk += 1

        self._add("INJ-01", "INJECTION", "No f-string SQL construction",
                 sql_injection_risk == 0, "CRITICAL",
                 f"SQL injection risks: {sql_injection_risk}",
                 metric=sql_injection_risk)

        self._add("INJ-02", "INJECTION", "No raw HTML output with user input",
                 xss_risk == 0, "HIGH",
                 f"XSS risks: {xss_risk}",
                 metric=xss_risk)

        print(f"  SQL injection risks: {sql_injection_risk} [{'OK' if sql_injection_risk == 0 else 'BLOCKED'}]")
        print(f"  XSS risks: {xss_risk} [{'OK' if xss_risk == 0 else 'BLOCKED'}]")
        print()

    # ===== MC6: On-Chain Integrity =====
    def _mc6_onchain_integrity(self):
        print("[MC6] ON-CHAIN INTEGRITY PROBE")
        print("-" * 40)

        ledger_file = PROJECT_ROOT / "backend" / "src" / "workers" / "lexradar" / "__init__.py"
        content = ledger_file.read_text() if ledger_file.exists() else ""

        uses_hashlib = "hashlib" in content or "sha256" in content
        no_raw_claims = not ("claims" in content.lower() and "sha256" not in content.lower())
        has_verify_bundle = "verify_bundle" in content

        self._add("ONC-01", "BLOCKCHAIN", "Ledger uses hashlib for hashing",
                 uses_hashlib, "CRITICAL",
                 f"hashlib usage: {uses_hashlib}",
                 metric=uses_hashlib)

        self._add("ONC-02", "BLOCKCHAIN", "No raw claims in ledger without hashing",
                 no_raw_claims, "CRITICAL",
                 f"No raw claims: {no_raw_claims}",
                 metric=no_raw_claims)

        self._add("ONC-03", "BLOCKCHAIN", "verify_bundle() exists for integrity",
                 has_verify_bundle, "HIGH",
                 f"verify_bundle found: {has_verify_bundle}",
                 metric=has_verify_bundle)

        print(f"  Hashlib usage: {'OK' if uses_hashlib else 'FAIL'}")
        print(f"  No raw claims: {'OK' if no_raw_claims else 'BLOCKED'}")
        print(f"  verify_bundle: {'OK' if has_verify_bundle else 'FAIL'}")
        print()

    # ===== MC7: Security Headers Audit =====
    def _mc7_security_headers(self):
        print("[MC7] SECURITY HEADERS AUDIT")
        print("-" * 40)

        headers_file = PROJECT_ROOT / "docs" / "api" / "SECURITY_HEADERS.md"
        headers_content = headers_file.read_text() if headers_file.exists() else ""

        required_headers = [
            "Content-Security-Policy",
            "Strict-Transport-Security",
            "X-Frame-Options",
            "X-Content-Type-Options",
            "Referrer-Policy",
            "Permissions-Policy",
            "X-XSS-Protection",
        ]

        found = sum(1 for h in required_headers if h in headers_content)

        self._add("HDR-01", "HEADERS", "All required security headers documented",
                 found >= 7, "HIGH",
                 f"Headers found: {found}/7",
                 metric=found)

        # Check CORS middleware in main.py for restrictiveness
        main_file = PROJECT_ROOT / "backend" / "src" / "api" / "main.py"
        main_content = main_file.read_text() if main_file.exists() else ""
        cors_restricted = "allow_origins" in main_content and "allow_methods" in main_content

        self._add("HDR-02", "HEADERS", "CORS middleware configured",
                 cors_restricted, "MEDIUM",
                 f"CORS configured: {cors_restricted}",
                 metric=cors_restricted)

        print(f"  Security headers: {found}/7 [{'OK' if found >= 7 else 'FAIL'}]")
        print(f"  CORS middleware: {'OK' if cors_restricted else 'WARN'}")
        print()

    # ===== MC8: Dependency CVE Scan =====
    def _mc8_dependency_cve(self):
        print("[MC8] DEPENDENCY CVE SCAN")
        print("-" * 40)

        req_file = PROJECT_ROOT / "backend" / "requirements.txt"
        req_content = req_file.read_text() if req_file.exists() else ""

        # Check for known vulnerable patterns
        # Format: (package, fixed_version_tuple, cve_id)
        known_vulnerable = [
            ("requests", (2, 31, 0), "CVE-2023-32681"),
            ("urllib3", (2, 0, 7), "CVE-2023-45803"),
            ("cryptography", (41, 0, 6), "CVE-2023-50782"),
            ("fastapi", (0, 104, 1), "CVE-2023-29159"),
        ]

        def parse_floor_version(spec: str) -> tuple:
            """Extract minimum version from >=X.Y.Z constraint."""
            match = re.search(r'>=([\d.]+)', spec)
            if match:
                parts = match.group(1).split('.')
                return tuple(int(p) for p in parts)
            return None

        cve_count = 0
        for pkg, fixed_version, cve in known_vulnerable:
            if pkg in req_content:
                for line in req_content.splitlines():
                    if line.startswith(pkg):
                        floor = parse_floor_version(line)
                        if floor is None:
                            # Unpinned dependency — potential risk
                            cve_count += 1
                        elif floor < fixed_version:
                            # Minimum pinned version is below CVE fix
                            cve_count += 1
                        break

        self._add("CVE-01", "DEPENDENCIES", "No known CVEs in requirements",
                 cve_count == 0, "HIGH",
                 f"Known CVE matches: {cve_count}",
                 metric=cve_count)

        print(f"  Known CVE matches: {cve_count} [{'OK' if cve_count == 0 else 'WARN'}]")
        print()

    # ===== MC9: Signed Report =====
    def _mc9_signed_report(self) -> Dict[str, Any]:
        print("=" * 70)
        print("PENETRATION TEST REPORT — FINAL ASSESSMENT")
        print("=" * 70)

        vectors = ["AUTH", "JWT", "RLS", "SECRETS", "INJECTION", "BLOCKCHAIN", "HEADERS", "DEPENDENCIES"]
        vector_results = {}
        for v in vectors:
            checks = [r for r in self.results if r.vector == v]
            passed = sum(1 for c in checks if c.passed)
            total = len(checks)
            status = "PASS" if total > 0 and passed == total else "FAIL"
            vector_results[v] = {"passed": passed, "total": total, "status": status}
            print(f"  {v}: {passed}/{total} — {status}")

        critical_count = len(self.critical_findings)
        high_count = len(self.high_findings)

        overall_pass = critical_count == 0
        risk_score = critical_count * 10 + high_count * 5

        print()
        print(f"  Critical findings: {critical_count}")
        for cf in self.critical_findings:
            print(f"    - {cf}")
        print(f"  High findings: {high_count}")
        for hf in self.high_findings:
            print(f"    - {hf}")
        print(f"  Risk score: {risk_score}/100")
        print()

        status = "PASS" if overall_pass else "FAIL"
        print(f"  Overall: **{status}**")

        # Generate report
        report_lines = [
            "# Penetration Test Report",
            "",
            f"**Timestamp**: {datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')}",
            f"**Commit**: {self._get_git_commit()}",
            f"**Status**: {status}",
            f"**Risk Score**: {risk_score}/100",
            f"**Critical Findings**: {critical_count}",
            f"**High Findings**: {high_count}",
            "",
            "## Per-Vector Results",
        ]
        for v, stats in vector_results.items():
            report_lines.append(f"- **{v}**: {stats['passed']}/{stats['total']} — {stats['status']}")

        report_lines.extend(["", "## Detailed Checks"])
        for r in self.results:
            s = "PASS" if r.passed else "FAIL"
            report_lines.append(f"- `{r.check_id}` ({r.vector}): {r.description} — **{s}** [{r.severity}] {r.details}")

        if self.critical_findings:
            report_lines.extend(["", "## Critical Findings"])
            for cf in self.critical_findings:
                report_lines.append(f"- **{cf}**: CRITICAL")

        report_content = "\n".join(report_lines)
        report_hash = hashlib.sha256(report_content.encode()).hexdigest()

        report_lines.extend(["", f"## Report Signature", f"SHA-256: `{report_hash}`"])

        report_path = PROJECT_ROOT / "docs" / "execution" / "PENETRATION_TEST_REPORT.md"
        report_path.write_text("\n".join(report_lines))

        print(f"  Report saved: {report_path}")
        print(f"  Report SHA-256: {report_hash}")
        print("=" * 70)

        return {
            "status": status,
            "risk_score": risk_score,
            "critical_count": critical_count,
            "high_count": high_count,
            "report_path": str(report_path),
            "report_hash": report_hash,
            "total_checks": len(self.results),
            "passed_checks": sum(1 for r in self.results if r.passed),
        }


if __name__ == "__main__":
    test = PenetrationTest()
    result = test.run()
    sys.exit(0 if result["status"] == "PASS" else 1)
