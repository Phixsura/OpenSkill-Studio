import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import DataExportScheduleCard from "../src/components/data-export-schedule-card";

const schedules = [
  {
    schedule_id: "s1",
    resource_type: "users",
    format: "csv",
    destination: "s3://bucket/exports",
    interval_hours: 24,
    enabled: true,
    run_count: 30,
    last_error: "",
  },
  {
    schedule_id: "s2",
    resource_type: "orders",
    format: "json",
    destination: "https://webhook.site/abc",
    interval_hours: 6,
    enabled: true,
    run_count: 120,
    last_error: "timeout",
  },
];

describe("DataExportScheduleCard", () => {
  it("renders header", () => {
    const { container } = render(<DataExportScheduleCard schedules={schedules} appName="My App" />);
    expect(container.textContent).toContain("Export Schedules");
  });

  it("shows active and error counts", () => {
    const { container } = render(<DataExportScheduleCard schedules={schedules} appName="App" />);
    expect(container.textContent).toContain("2 active");
    expect(container.textContent).toContain("1 errors");
  });

  it("renders resource types and formats", () => {
    const { container } = render(<DataExportScheduleCard schedules={schedules} appName="App" />);
    expect(container.textContent).toContain("users");
    expect(container.textContent).toContain("csv");
    expect(container.textContent).toContain("orders");
  });

  it("shows interval and run count", () => {
    const { container } = render(<DataExportScheduleCard schedules={schedules} appName="App" />);
    expect(container.textContent).toContain("every 24h");
    expect(container.textContent).toContain("30 runs");
  });

  it("shows error message", () => {
    const { container } = render(<DataExportScheduleCard schedules={schedules} appName="App" />);
    expect(container.textContent).toContain("timeout");
  });

  it("shows empty state", () => {
    const { container } = render(<DataExportScheduleCard schedules={[]} appName="App" />);
    expect(container.textContent).toContain("No export schedules");
  });
});
