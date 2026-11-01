import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import UsageAlertCard from "../src/components/usage-alert-card";

const alerts = [
  {
    metric: "api_calls",
    level: "ok" as const,
    used: 500,
    limit: 1000,
    usage_pct: 50,
    acknowledged: false,
  },
  {
    metric: "storage_mb",
    level: "warning" as const,
    used: 420,
    limit: 500,
    usage_pct: 84,
    acknowledged: false,
  },
  {
    metric: "webhooks",
    level: "critical" as const,
    used: 98,
    limit: 100,
    usage_pct: 98,
    acknowledged: true,
  },
];

describe("UsageAlertCard", () => {
  it("renders header and app name", () => {
    const { container } = render(<UsageAlertCard alerts={alerts} appName="My App" />);
    expect(container.textContent).toContain("Usage Alerts");
    expect(container.textContent).toContain("My App");
  });

  it("shows active alert count", () => {
    const { container } = render(<UsageAlertCard alerts={alerts} appName="App" />);
    expect(container.textContent).toContain("2 alerts");
  });

  it("shows all-clear when no alerts", () => {
    const okAlerts = [alerts[0]];
    const { container } = render(<UsageAlertCard alerts={okAlerts} appName="App" />);
    expect(container.textContent).toContain("All clear");
  });

  it("renders metric names with spaces", () => {
    const { container } = render(<UsageAlertCard alerts={alerts} appName="App" />);
    expect(container.textContent).toContain("api calls");
    expect(container.textContent).toContain("storage mb");
  });

  it("shows usage values and percentage", () => {
    const { container } = render(<UsageAlertCard alerts={alerts} appName="App" />);
    expect(container.textContent).toContain("500 / 1.0K");
    expect(container.textContent).toContain("98%");
  });

  it("shows level labels", () => {
    const { container } = render(<UsageAlertCard alerts={alerts} appName="App" />);
    expect(container.textContent).toContain("ok");
    expect(container.textContent).toContain("warning");
    expect(container.textContent).toContain("critical");
  });

  it("shows ack label", () => {
    const { container } = render(<UsageAlertCard alerts={alerts} appName="App" />);
    expect(container.textContent).toContain("ack");
  });

  it("shows empty state", () => {
    const { container } = render(<UsageAlertCard alerts={[]} appName="App" />);
    expect(container.textContent).toContain("No usage metrics monitored");
  });
});
