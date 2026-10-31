import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { UptimeMonitorBar } from "@/components/uptime-monitor-bar";

describe("UptimeMonitorBar", () => {
  const days = [
    { date: "2026-10-01", status: "up", color: "green" },
    { date: "2026-10-02", status: "degraded", color: "yellow" },
  ];
  it("renders uptime bar", () => {
    const { container } = render(
      <UptimeMonitorBar serviceName="API Gateway" days={days} uptimePct={96.67} nines="96.67%" />
    );
    expect(container.textContent).toContain("API Gateway");
    expect(container.textContent).toContain("96.67%");
    expect(container.textContent).toContain("2 days");
  });
});
