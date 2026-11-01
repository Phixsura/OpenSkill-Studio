import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import DataExportCard from "../src/components/data-export-card";

const completedExport = {
  export_id: "exp-1",
  resource_type: "users",
  format: "csv" as const,
  status: "completed" as const,
  created_at: new Date(Date.now() - 3_600_000).toISOString(),
  file_size_bytes: 2048000,
  row_count: 15000,
  error_message: null,
};

const processingExport = {
  export_id: "exp-2",
  resource_type: "events",
  format: "json" as const,
  status: "processing" as const,
  created_at: new Date(Date.now() - 60_000).toISOString(),
  file_size_bytes: 0,
  row_count: 0,
  error_message: null,
};

const failedExport = {
  export_id: "exp-3",
  resource_type: "analytics",
  format: "parquet" as const,
  status: "failed" as const,
  created_at: new Date(Date.now() - 7_200_000).toISOString(),
  file_size_bytes: 0,
  row_count: 0,
  error_message: "timeout exceeded",
};

const expiredExport = {
  export_id: "exp-4",
  resource_type: "logs",
  format: "json" as const,
  status: "expired" as const,
  created_at: new Date(Date.now() - 86_400_000).toISOString(),
  file_size_bytes: 0,
  row_count: 0,
  error_message: null,
};

describe("DataExportCard", () => {
  it("renders header and app name", () => {
    const { container } = render(<DataExportCard exports={[completedExport]} appName="My App" />);
    expect(container.textContent).toContain("Data Exports");
    expect(container.textContent).toContain("My App");
  });

  it("shows in-progress badge", () => {
    const { container } = render(<DataExportCard exports={[processingExport]} appName="App" />);
    expect(container.textContent).toContain("1 in progress");
  });

  it("renders resource type and format badge", () => {
    const { container } = render(<DataExportCard exports={[completedExport]} appName="App" />);
    expect(container.textContent).toContain("users");
    expect(container.textContent).toContain("csv");
  });

  it("shows row count and file size for completed", () => {
    const { container } = render(<DataExportCard exports={[completedExport]} appName="App" />);
    expect(container.textContent).toContain("15,000 rows");
    expect(container.textContent).toContain("2.0 MB");
  });

  it("shows error message for failed", () => {
    const { container } = render(<DataExportCard exports={[failedExport]} appName="App" />);
    expect(container.textContent).toContain("timeout exceeded");
    expect(container.textContent).toContain("failed");
  });

  it("renders format badges for all types", () => {
    const { container } = render(
      <DataExportCard exports={[completedExport, processingExport, failedExport]} appName="App" />,
    );
    expect(container.textContent).toContain("csv");
    expect(container.textContent).toContain("json");
    expect(container.textContent).toContain("parquet");
  });

  it("shows status icons", () => {
    const { container } = render(
      <DataExportCard exports={[completedExport, failedExport, expiredExport]} appName="App" />,
    );
    expect(container.textContent).toContain("✅");
    expect(container.textContent).toContain("❌");
    expect(container.textContent).toContain("🕐");
  });

  it("shows empty state", () => {
    const { container } = render(<DataExportCard exports={[]} appName="App" />);
    expect(container.textContent).toContain("No exports");
  });
});
