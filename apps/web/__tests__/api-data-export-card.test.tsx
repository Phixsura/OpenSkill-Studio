import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDataExportCard from "../src/components/api-data-export-card";

const exps = [
  { export_id: "e1", format: "csv", resource: "users", status: "completed" as const, record_count: 5000, file_size_bytes: 1048576 },
  { export_id: "e2", format: "json", resource: "apps", status: "pending" as const, record_count: 0, file_size_bytes: 0 },
];

describe("APIDataExportCard", () => {
  it("renders header and count", () => {
    const { container } = render(<APIDataExportCard exports={exps} appName="App" />);
    expect(container.textContent).toContain("Data Exports");
    expect(container.textContent).toContain("2 exports");
  });

  it("shows status and format", () => {
    const { container } = render(<APIDataExportCard exports={exps} appName="App" />);
    expect(container.textContent).toContain("completed");
    expect(container.textContent).toContain("csv");
    expect(container.textContent).toContain("5000 rows");
  });

  it("shows empty state", () => {
    const { container } = render(<APIDataExportCard exports={[]} appName="App" />);
    expect(container.textContent).toContain("No data exports");
  });
});
