import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-data-export-card";

describe("DataExportCard", () => {
  it("shows exports", () => {
    const exports = [{ job_id: "j1", consumer_id: "c1", format: "json", status: "completed", data_types: ["usage"], record_count: 5000, file_size_kb: 1024 }];
    const { container } = render(<Card exports={exports} appName="App" />);
    expect(container.textContent).toContain("Data Exports");
    expect(container.textContent).toContain("c1");
    expect(container.textContent).toContain("JSON");
    expect(container.textContent).toContain("5,000 records");
  });
  it("shows empty", () => {
    const { container } = render(<Card exports={[]} appName="App" />);
    expect(container.textContent).toContain("No exports");
  });
});
