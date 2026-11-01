"""Tests for App Data Export Pipeline — lifecycle, PII redaction, formats, limits."""

import json
from datetime import UTC, datetime, timedelta

import pytest

from app.services.app_data_export_pipeline import (
    AppDataExportPipeline,
    ExportFormat,
    ExportStatus,
    MAX_ROWS,
    PIIField,
)

SAMPLE_ROWS = [
    {"id": "u1", "name": "Alice Johnson", "email": "alice@example.com", "ip_address": "192.168.1.1", "score": 95},
    {"id": "u2", "name": "Bob Smith", "email": "bob@test.org", "ip_address": "10.0.0.5", "score": 87},
]


class TestLifecycle:
    def test_request_creates_job(self):
        p = AppDataExportPipeline()
        r = p.request_export("inst-1", "admin")
        assert r.success is True
        job = p.get_job(r.job_id, "admin")
        assert job.status == ExportStatus.REQUESTED

    def test_process_sets_ready(self):
        p = AppDataExportPipeline()
        r = p.request_export("inst-1", "admin")
        pr = p.process_export(r.job_id, SAMPLE_ROWS)
        assert pr.success is True
        job = p.get_job(r.job_id, "admin")
        assert job.status == ExportStatus.READY
        assert job.row_count == 2
        assert job.byte_size > 0

    def test_download_returns_output(self):
        p = AppDataExportPipeline()
        r = p.request_export("inst-1", "admin")
        p.process_export(r.job_id, SAMPLE_ROWS)
        output, err = p.download(r.job_id, "admin")
        assert err is None
        assert output is not None
        assert "Alice" in output  # not redacted (no PII fields specified)

    def test_download_sets_downloaded(self):
        p = AppDataExportPipeline()
        r = p.request_export("inst-1", "admin")
        p.process_export(r.job_id, SAMPLE_ROWS)
        p.download(r.job_id, "admin")
        assert p.get_job(r.job_id, "admin").status == ExportStatus.DOWNLOADED

    def test_download_wrong_user_denied(self):
        p = AppDataExportPipeline()
        r = p.request_export("inst-1", "admin")
        p.process_export(r.job_id, SAMPLE_ROWS)
        _, err = p.download(r.job_id, "hacker")
        assert err == "Access denied"

    def test_download_not_ready(self):
        p = AppDataExportPipeline()
        r = p.request_export("inst-1", "admin")
        _, err = p.download(r.job_id, "admin")
        assert "not ready" in err

    def test_nonexistent_job(self):
        p = AppDataExportPipeline()
        assert p.get_job("nope", "admin") is None
        _, err = p.download("nope", "admin")
        assert err == "Job not found"


class TestPIIRedaction:
    def test_email_redacted(self):
        p = AppDataExportPipeline()
        r = p.request_export("inst-1", "admin", pii_fields=[PIIField.EMAIL])
        p.process_export(r.job_id, SAMPLE_ROWS)
        output, _ = p.download(r.job_id, "admin")
        data = json.loads(output)
        assert "alice@example.com" not in output
        assert "***@example.com" in data[0]["email"]

    def test_name_redacted(self):
        p = AppDataExportPipeline()
        r = p.request_export("inst-1", "admin", pii_fields=[PIIField.NAME])
        p.process_export(r.job_id, SAMPLE_ROWS)
        output, _ = p.download(r.job_id, "admin")
        data = json.loads(output)
        assert data[0]["name"].startswith("A")
        assert "***" in data[0]["name"]

    def test_ip_redacted(self):
        p = AppDataExportPipeline()
        r = p.request_export("inst-1", "admin", pii_fields=[PIIField.IP_ADDRESS])
        p.process_export(r.job_id, SAMPLE_ROWS)
        output, _ = p.download(r.job_id, "admin")
        assert "192.168.1.1" not in output
        assert "xxx.xxx.xxx.xxx" in output

    def test_multiple_pii_fields(self):
        p = AppDataExportPipeline()
        r = p.request_export("inst-1", "admin",
                              pii_fields=[PIIField.EMAIL, PIIField.NAME, PIIField.IP_ADDRESS])
        p.process_export(r.job_id, SAMPLE_ROWS)
        output, _ = p.download(r.job_id, "admin")
        assert "alice@example.com" not in output
        assert "Alice Johnson" not in output
        assert "192.168.1.1" not in output

    def test_no_pii_fields_no_redaction(self):
        p = AppDataExportPipeline()
        r = p.request_export("inst-1", "admin", pii_fields=[])
        p.process_export(r.job_id, SAMPLE_ROWS)
        output, _ = p.download(r.job_id, "admin")
        assert "alice@example.com" in output

    def test_phone_redacted(self):
        p = AppDataExportPipeline()
        rows = [{"phone": "+1-555-867-5309"}]
        r = p.request_export("inst-1", "admin", pii_fields=[PIIField.PHONE])
        p.process_export(r.job_id, rows)
        output, _ = p.download(r.job_id, "admin")
        data = json.loads(output)
        assert data[0]["phone"].startswith("***")
        assert data[0]["phone"].endswith("5309")


class TestFormats:
    def test_json_format(self):
        p = AppDataExportPipeline()
        r = p.request_export("inst-1", "admin", export_format=ExportFormat.JSON)
        p.process_export(r.job_id, SAMPLE_ROWS)
        output, _ = p.download(r.job_id, "admin")
        data = json.loads(output)
        assert isinstance(data, list)
        assert len(data) == 2

    def test_csv_format(self):
        p = AppDataExportPipeline()
        r = p.request_export("inst-1", "admin", export_format=ExportFormat.CSV)
        p.process_export(r.job_id, SAMPLE_ROWS)
        output, _ = p.download(r.job_id, "admin")
        lines = output.strip().split("\n")
        assert len(lines) == 3  # header + 2 rows
        assert "id" in lines[0]
        assert "alice@example.com" in output

    def test_empty_rows(self):
        p = AppDataExportPipeline()
        r = p.request_export("inst-1", "admin")
        p.process_export(r.job_id, [])
        job = p.get_job(r.job_id, "admin")
        assert job.row_count == 0
        assert job.status == ExportStatus.READY


class TestLimits:
    def test_row_limit_exceeded(self):
        p = AppDataExportPipeline()
        r = p.request_export("inst-1", "admin")
        rows = [{"id": i} for i in range(MAX_ROWS + 1)]
        pr = p.process_export(r.job_id, rows)
        assert pr.success is False
        assert "exceeds limit" in pr.error
        assert p.get_job(r.job_id, "admin").status == ExportStatus.FAILED

    def test_process_wrong_status(self):
        p = AppDataExportPipeline()
        r = p.request_export("inst-1", "admin")
        p.process_export(r.job_id, SAMPLE_ROWS)
        pr = p.process_export(r.job_id, SAMPLE_ROWS)  # already processed
        assert pr.success is False


class TestExpiry:
    def test_expired_download_blocked(self):
        p = AppDataExportPipeline()
        r = p.request_export("inst-1", "admin")
        p.process_export(r.job_id, SAMPLE_ROWS)
        job = p.get_job(r.job_id, "admin")
        job.expires_at = datetime.now(UTC) - timedelta(hours=1)
        _, err = p.download(r.job_id, "admin")
        assert "expired" in err

    def test_cleanup_expired(self):
        p = AppDataExportPipeline()
        r = p.request_export("inst-1", "admin")
        p.process_export(r.job_id, SAMPLE_ROWS)
        job = p.get_job(r.job_id, "admin")
        job.expires_at = datetime.now(UTC) - timedelta(hours=1)
        count = p.cleanup_expired()
        assert count == 1
        assert job.output is None


class TestListing:
    def test_list_jobs(self):
        p = AppDataExportPipeline()
        p.request_export("inst-1", "admin")
        p.request_export("inst-1", "admin")
        p.request_export("inst-2", "admin")
        jobs = p.list_jobs("inst-1", "admin")
        assert len(jobs) == 2

    def test_list_jobs_scoped_to_user(self):
        p = AppDataExportPipeline()
        p.request_export("inst-1", "admin")
        p.request_export("inst-1", "other-admin")
        assert len(p.list_jobs("inst-1", "admin")) == 1
        assert len(p.list_jobs("inst-1", "other-admin")) == 1


class TestScopedAccess:
    def test_get_job_wrong_user_returns_none(self):
        p = AppDataExportPipeline()
        r = p.request_export("inst-1", "admin")
        assert p.get_job(r.job_id, "hacker") is None

    def test_get_job_correct_user(self):
        p = AppDataExportPipeline()
        r = p.request_export("inst-1", "admin")
        assert p.get_job(r.job_id, "admin") is not None


class TestCSVFormulaInjection:
    def test_formula_prefix_escaped(self):
        p = AppDataExportPipeline()
        rows = [{"name": "=cmd|'/C calc'!A0", "safe": "hello"}]
        r = p.request_export("inst-1", "admin", export_format=ExportFormat.CSV)
        p.process_export(r.job_id, rows)
        output, _ = p.download(r.job_id, "admin")
        # The dangerous value is prefixed with a quote to neutralize formula
        data_row = output.split("\n")[1]
        assert data_row.startswith("'=") or "'=cmd" in data_row

    def test_plus_prefix_escaped(self):
        p = AppDataExportPipeline()
        rows = [{"val": "+1-555-0100"}]
        r = p.request_export("inst-1", "admin", export_format=ExportFormat.CSV)
        p.process_export(r.job_id, rows)
        output, _ = p.download(r.job_id, "admin")
        assert "'+1-555-0100" in output

    def test_safe_values_unchanged(self):
        p = AppDataExportPipeline()
        rows = [{"name": "Alice", "score": "95"}]
        r = p.request_export("inst-1", "admin", export_format=ExportFormat.CSV)
        p.process_export(r.job_id, rows)
        output, _ = p.download(r.job_id, "admin")
        assert "Alice" in output
        assert "'Alice" not in output
