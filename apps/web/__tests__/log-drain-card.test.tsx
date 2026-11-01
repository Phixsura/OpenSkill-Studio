import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import LogDrainCard from "../src/components/log-drain-card";

const drains = [
  {
    drain_id: "datadog",
    destination: "https://intake.datadoghq.com",
    drain_type: "http",
    min_level: "warn",
    enabled: true,
    stats: { sent: 500, failed: 3, dropped: 0, success_rate: 99.4 },
  },
  {
    drain_id: "syslog-backup",
    destination: "syslog://10.0.0.1:514",
    drain_type: "syslog",
    min_level: "error",
    enabled: false,
    stats: { sent: 0, failed: 0, dropped: 0, success_rate: 100 },
  },
];

describe("LogDrainCard", () => {
  it("renders header and counts", () => {
    const { container } = render(<LogDrainCard drains={drains} appName="App" />);
    expect(container.textContent).toContain("Log Drains");
    expect(container.textContent).toContain("1 active / 2 total");
  });

  it("shows drain IDs and types", () => {
    const { container } = render(<LogDrainCard drains={drains} appName="App" />);
    expect(container.textContent).toContain("datadog");
    expect(container.textContent).toContain("http");
    expect(container.textContent).toContain("syslog");
  });

  it("shows min level", () => {
    const { container } = render(<LogDrainCard drains={drains} appName="App" />);
    expect(container.textContent).toContain("warn+");
    expect(container.textContent).toContain("error+");
  });

  it("shows delivery stats", () => {
    const { container } = render(<LogDrainCard drains={drains} appName="App" />);
    expect(container.textContent).toContain("99.4%");
    expect(container.textContent).toContain("500 sent");
  });

  it("shows empty state", () => {
    const { container } = render(<LogDrainCard drains={[]} appName="App" />);
    expect(container.textContent).toContain("No log drains");
  });
});
