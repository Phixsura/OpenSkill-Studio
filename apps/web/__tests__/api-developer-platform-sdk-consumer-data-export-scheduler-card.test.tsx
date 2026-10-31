import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-consumer-data-export-scheduler-card";

describe("DataExportSchedulerCard", () => {
  it("shows schedules", () => {
    const schedules = [{ id: "s1", dataType: "logs", format: "csv", frequency: "daily", enabled: true, lastRun: "2026-06-01" }];
    const { container } = render(<Card schedules={schedules} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("Export Scheduler");
    expect(container.textContent).toContain("logs");
    expect(container.textContent).toContain("csv");
    expect(container.textContent).toContain("daily");
    expect(container.textContent).toContain("ON");
  });
  it("shows empty", () => {
    const { container } = render(<Card schedules={[]} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("No export schedules");
  });
});
