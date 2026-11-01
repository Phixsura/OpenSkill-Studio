import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ScheduledReportCard from "../src/components/scheduled-report-card";

const reports = [
  {
    report_id: "r1",
    name: "Weekly Summary",
    schedule: "weekly",
    format: "pdf",
    recipients: ["admin@x.com", "cto@x.com"],
    enabled: true,
    generation_count: 12,
  },
  {
    report_id: "r2",
    name: "Daily Metrics",
    schedule: "daily",
    format: "csv",
    recipients: ["ops@x.com"],
    enabled: false,
    generation_count: 30,
  },
];

describe("ScheduledReportCard", () => {
  it("renders header", () => {
    const { container } = render(<ScheduledReportCard reports={reports} appName="My App" />);
    expect(container.textContent).toContain("Scheduled Reports");
  });

  it("shows active count", () => {
    const { container } = render(<ScheduledReportCard reports={reports} appName="App" />);
    expect(container.textContent).toContain("1 active");
  });

  it("renders report names and schedules", () => {
    const { container } = render(<ScheduledReportCard reports={reports} appName="App" />);
    expect(container.textContent).toContain("Weekly Summary");
    expect(container.textContent).toContain("weekly");
    expect(container.textContent).toContain("daily");
  });

  it("shows recipients", () => {
    const { container } = render(<ScheduledReportCard reports={reports} appName="App" />);
    expect(container.textContent).toContain("admin@x.com");
  });

  it("shows generation count", () => {
    const { container } = render(<ScheduledReportCard reports={reports} appName="App" />);
    expect(container.textContent).toContain("12 sent");
  });

  it("shows empty state", () => {
    const { container } = render(<ScheduledReportCard reports={[]} appName="App" />);
    expect(container.textContent).toContain("No scheduled reports");
  });
});
