import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { UptimeMonitorPanel } from "@/components/uptime-monitor-panel";

const services = [
  { service: "API Gateway", uptimePct: 99.99, currentStreak: 5000, sla99: true, sla999: true, sla9999: true },
  { service: "Database", uptimePct: 99.5, currentStreak: 100, sla99: true, sla999: false, sla9999: false },
];

describe("UptimeMonitorPanel", () => {
  it("renders uptime stats", () => {
    const { container } = render(<UptimeMonitorPanel services={services} overallUptime={99.75} />);
    expect(container.textContent).toContain("API Gateway");
    expect(container.textContent).toContain("99.99%");
    expect(container.textContent).toContain("99.75%");
  });
});
