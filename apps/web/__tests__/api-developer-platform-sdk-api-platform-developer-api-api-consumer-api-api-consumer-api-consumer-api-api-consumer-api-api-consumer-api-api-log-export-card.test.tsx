import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-api-consumer-api-api-consumer-api-api-log-export-card";

describe("ConsumerApiLogExportCard", () => {
  it("shows jobs", () => {
    const jobs = [{ id: "j1", format: "json", recordCount: 500, status: "completed", startTime: "12:00", endTime: "13:00" }];
    const { container } = render(<Card jobs={jobs} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("Log Export");
    expect(container.textContent).toContain("JSON");
    expect(container.textContent).toContain("500 records");
    expect(container.textContent).toContain("completed");
  });
  it("shows empty", () => {
    const { container } = render(<Card jobs={[]} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("No exports");
  });
});
