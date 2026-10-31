import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-data-export-card";

describe("ConsumerDataExportCard", () => {
  it("shows exports", () => {
    const exports = [{ id: "ex1", format: "json", status: "completed", recordCount: 150, sizeBytes: 2048, createdAt: "2026-06-01" }];
    const { container } = render(<Card exports={exports} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("Data Exports");
    expect(container.textContent).toContain("JSON");
    expect(container.textContent).toContain("150 records");
    expect(container.textContent).toContain("2.0 KB");
    expect(container.textContent).toContain("completed");
  });
  it("shows empty", () => {
    const { container } = render(<Card exports={[]} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("No exports");
  });
});
