import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDataExportManagerCard from "../src/components/api-developer-api-api-data-export-manager-card";

const jobs = [
  { job_id: "j1", export_type: "usage", format: "csv", status: "completed", row_count: 50000, file_size_bytes: 2097152 },
  { job_id: "j2", export_type: "logs", format: "json", status: "running", row_count: 0, file_size_bytes: 0 },
];

describe("APIDeveloperAPIApiDataExportManagerCard", () => {
  it("shows export jobs", () => {
    const { container } = render(<APIDeveloperAPIApiDataExportManagerCard jobs={jobs} appName="App" />);
    expect(container.textContent).toContain("Data Exports");
    expect(container.textContent).toContain("usage");
    expect(container.textContent).toContain(".csv");
    expect(container.textContent).toContain("50,000 rows");
    expect(container.textContent).toContain("2.0MB");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiDataExportManagerCard jobs={[]} appName="App" />);
    expect(container.textContent).toContain("No export jobs");
  });
});
