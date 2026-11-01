"""Tests for App Content Scanner — secrets, unsafe code, URLs, sizes, dependencies."""

import pytest

from app.services.app_content_scanner import (
    AppContentScanner,
    FindingCategory,
    FindingSeverity,
    MAX_FILE_COUNT,
)


class TestSecretDetection:
    def test_api_key_detected(self):
        scanner = AppContentScanner()
        files = {"config.py": 'API_KEY = "sk_live_abcdef1234567890abcdef"'}
        result = scanner.scan("app-1", files)
        assert any(f.category == FindingCategory.SECRET_LEAK for f in result.findings)
        assert not result.passed

    def test_password_detected(self):
        scanner = AppContentScanner()
        files = {"settings.py": 'password = "SuperSecret123!"'}
        result = scanner.scan("app-1", files)
        assert any("Password" in f.message for f in result.findings)

    def test_github_token_detected(self):
        scanner = AppContentScanner()
        files = {"deploy.sh": "TOKEN=ghp_ABCDEFghijklmnopqrstuvwxyz0123456789"}
        result = scanner.scan("app-1", files)
        assert any("GitHub" in (f.pattern_matched or "") for f in result.findings)

    def test_private_key_detected(self):
        scanner = AppContentScanner()
        files = {"key.pem": "-----BEGIN RSA PRIVATE KEY-----\nMIIE..."}
        result = scanner.scan("app-1", files)
        assert any("Private key" in (f.pattern_matched or "") for f in result.findings)

    def test_clean_code_passes(self):
        scanner = AppContentScanner()
        files = {"main.py": "def hello():\n    return 'world'"}
        result = scanner.scan("app-1", files)
        assert len(result.findings) == 0
        assert result.passed is True


class TestUnsafeCode:
    # Note: these patterns detect eval/exec/os.system in SCANNED app code,
    # the scanner itself never calls these functions.
    def test_eval_detected(self):
        scanner = AppContentScanner()
        files = {"handler.py": "result = eval(user_input)"}
        result = scanner.scan("app-1", files)
        assert any(f.category == FindingCategory.UNSAFE_CODE for f in result.findings)
        assert any("eval" in (f.pattern_matched or "") for f in result.findings)

    def test_exec_detected(self):
        scanner = AppContentScanner()
        files = {"run.py": "exec(code_string)"}
        result = scanner.scan("app-1", files)
        assert any("exec" in (f.pattern_matched or "") for f in result.findings)

    def test_subprocess_detected(self):
        scanner = AppContentScanner()
        files = {"cmd.py": "subprocess.run(['ls', '-la'])"}
        result = scanner.scan("app-1", files)
        assert any("Subprocess" in (f.pattern_matched or "") for f in result.findings)

    def test_safe_code_no_findings(self):
        scanner = AppContentScanner()
        files = {"app.py": "x = evaluate_score(data)\nresult = executor.submit(task)"}
        result = scanner.scan("app-1", files)
        # "evaluate_score" and "executor" should NOT trigger
        assert not any(f.category == FindingCategory.UNSAFE_CODE for f in result.findings)


class TestURLValidation:
    def test_localhost_detected(self):
        scanner = AppContentScanner()
        files = {"config.json": '{"api": "http://localhost:3000/api"}'}
        result = scanner.scan("app-1", files)
        assert any(f.category == FindingCategory.INVALID_URL for f in result.findings)

    def test_internal_ip_detected(self):
        scanner = AppContentScanner()
        files = {"config.yaml": "url: http://192.168.1.100:8080"}
        result = scanner.scan("app-1", files)
        assert any(f.category == FindingCategory.INVALID_URL for f in result.findings)

    def test_public_url_passes(self):
        scanner = AppContentScanner()
        files = {"config.json": '{"api": "https://api.example.com"}'}
        result = scanner.scan("app-1", files)
        assert not any(f.category == FindingCategory.INVALID_URL for f in result.findings)


class TestSizeLimits:
    def test_large_file_flagged(self):
        scanner = AppContentScanner()
        files = {"big.bin": "x" * (11 * 1024 * 1024)}  # 11MB
        result = scanner.scan("app-1", files)
        assert any(f.category == FindingCategory.SIZE_LIMIT for f in result.findings)

    def test_too_many_files(self):
        scanner = AppContentScanner()
        files = {f"file_{i}.txt": "content" for i in range(MAX_FILE_COUNT + 1)}
        result = scanner.scan("app-1", files)
        assert any("Too many files" in f.message for f in result.findings)

    def test_normal_size_passes(self):
        scanner = AppContentScanner()
        files = {"small.txt": "hello world"}
        result = scanner.scan("app-1", files)
        assert not any(f.category == FindingCategory.SIZE_LIMIT for f in result.findings)


class TestDependencies:
    def test_malicious_dep_detected(self):
        scanner = AppContentScanner()
        result = scanner.scan("app-1", {}, dependencies=["lodash", "event-stream", "express"])
        assert any(f.category == FindingCategory.KNOWN_VULN for f in result.findings)
        assert not result.passed

    def test_clean_deps_pass(self):
        scanner = AppContentScanner()
        result = scanner.scan("app-1", {}, dependencies=["react", "express", "lodash"])
        assert not any(f.category == FindingCategory.KNOWN_VULN for f in result.findings)

    def test_no_deps_passes(self):
        scanner = AppContentScanner()
        result = scanner.scan("app-1", {"main.py": "pass"})
        assert result.passed is True


class TestScanResult:
    def test_files_scanned_count(self):
        scanner = AppContentScanner()
        files = {"a.py": "x=1", "b.py": "y=2", "c.py": "z=3"}
        result = scanner.scan("app-1", files)
        assert result.files_scanned == 3

    def test_total_bytes(self):
        scanner = AppContentScanner()
        files = {"a.txt": "hello"}
        result = scanner.scan("app-1", files)
        assert result.total_bytes == 5

    def test_critical_count(self):
        scanner = AppContentScanner()
        files = {"leak.py": 'api_key = "sk_test_1234567890abcdef"'}
        result = scanner.scan("app-1", files)
        assert result.critical_count >= 1

    def test_line_numbers_reported(self):
        scanner = AppContentScanner()
        files = {"code.py": "safe = True\napi_key = 'sk_test_abcdefghijklmnop'"}
        result = scanner.scan("app-1", files)
        secret_findings = [f for f in result.findings if f.category == FindingCategory.SECRET_LEAK]
        assert len(secret_findings) >= 1
        assert secret_findings[0].line_number == 2

    def test_file_path_reported(self):
        scanner = AppContentScanner()
        files = {"src/config.py": 'password = "hunter2hunter2"'}
        result = scanner.scan("app-1", files)
        assert result.findings[0].file_path == "src/config.py"
