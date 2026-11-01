import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DataExportPanel } from "@/components/data-export-panel";

const MOCK_JOBS = [
  {
    job_id: "e1",
    status: "ready" as const,
    export_format: "json" as const,
    row_count: 1500,
    byte_size: 245000,
    requested_at: "2026-10-28T10:00:00Z",
    completed_at: "2026-10-28T10:01:00Z",
    error: null,
  },
  {
    job_id: "e2",
    status: "downloaded" as const,
    export_format: "csv" as const,
    row_count: 500,
    byte_size: 32000,
    requested_at: "2026-10-27T08:00:00Z",
    completed_at: "2026-10-27T08:00:30Z",
    error: null,
  },
  {
    job_id: "e3",
    status: "failed" as const,
    export_format: "json" as const,
    row_count: 0,
    byte_size: 0,
    requested_at: "2026-10-26T12:00:00Z",
    completed_at: null,
    error: "Row count exceeds limit",
  },
];

const defaultProps = {
  jobs: MOCK_JOBS,
  onRequestExport: vi.fn(),
  onDownload: vi.fn(),
};

describe("DataExportPanel", () => {
  it("renders heading and count", () => {
    const { container } = render(<DataExportPanel {...defaultProps} />);
    expect(container.textContent).toContain("Data Export");
    expect(container.textContent).toContain("3 exports");
  });

  it("renders status badges", () => {
    const { container } = render(<DataExportPanel {...defaultProps} />);
    expect(container.textContent).toContain("Ready");
    expect(container.textContent).toContain("Downloaded");
    expect(container.textContent).toContain("Failed");
  });

  it("renders format labels", () => {
    const { container } = render(<DataExportPanel {...defaultProps} />);
    expect(container.textContent).toContain("JSON");
    expect(container.textContent).toContain("CSV");
  });

  it("renders row counts and sizes", () => {
    const { container } = render(<DataExportPanel {...defaultProps} />);
    expect(container.textContent).toContain("1,500 rows");
    expect(container.textContent).toContain("239.3 KB");
  });

  it("shows error for failed jobs", () => {
    const { container } = render(<DataExportPanel {...defaultProps} />);
    expect(container.textContent).toContain("Row count exceeds limit");
  });

  it("shows Download button for ready jobs only", () => {
    const { container } = render(<DataExportPanel {...defaultProps} />);
    const dlBtns = Array.from(container.querySelectorAll("button")).filter(
      (b) => b.textContent === "Download",
    );
    assert(dlBtns.length === 1); // only e1 is "ready"
  });

  it("calls onDownload", () => {
    const onDownload = vi.fn();
    const { container } = render(<DataExportPanel {...defaultProps} onDownload={onDownload} />);
    const dlBtn = Array.from(container.querySelectorAll("button")).find(
      (b) => b.textContent === "Download",
    );
    fireEvent.click(dlBtn!);
    expect(onDownload).toHaveBeenCalledWith("e1");
  });

  it("calls onRequestExport with format and PII flag", () => {
    const onRequestExport = vi.fn();
    const { container } = render(
      <DataExportPanel {...defaultProps} onRequestExport={onRequestExport} />,
    );
    const exportBtn = Array.from(container.querySelectorAll("button")).find(
      (b) => b.textContent === "Export",
    );
    fireEvent.click(exportBtn!);
    expect(onRequestExport).toHaveBeenCalledWith("json", true); // default: json + redact
  });

  it("switches format to CSV", () => {
    const onRequestExport = vi.fn();
    const { container } = render(
      <DataExportPanel {...defaultProps} onRequestExport={onRequestExport} />,
    );
    const select = container.querySelector(
      "select[aria-label='Export format']",
    ) as HTMLSelectElement;
    fireEvent.change(select, { target: { value: "csv" } });
    fireEvent.click(
      Array.from(container.querySelectorAll("button")).find((b) => b.textContent === "Export")!,
    );
    expect(onRequestExport).toHaveBeenCalledWith("csv", true);
  });

  it("toggles PII redaction off", () => {
    const onRequestExport = vi.fn();
    const { container } = render(
      <DataExportPanel {...defaultProps} onRequestExport={onRequestExport} />,
    );
    const checkbox = container.querySelector("input[type='checkbox']") as HTMLInputElement;
    fireEvent.click(checkbox); // uncheck
    fireEvent.click(
      Array.from(container.querySelectorAll("button")).find((b) => b.textContent === "Export")!,
    );
    expect(onRequestExport).toHaveBeenCalledWith("json", false);
  });

  it("shows exporting state", () => {
    const { container } = render(<DataExportPanel {...defaultProps} exporting />);
    expect(container.textContent).toContain("Exporting…");
  });

  it("shows empty state", () => {
    const { container } = render(<DataExportPanel {...defaultProps} jobs={[]} />);
    expect(container.textContent).toContain("No exports yet");
  });

  it("renders format selector", () => {
    const { container } = render(<DataExportPanel {...defaultProps} />);
    const select = container.querySelector("select");
    expect(select).toBeTruthy();
  });
});
