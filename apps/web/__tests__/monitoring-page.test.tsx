import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MonitoringPage } from "@/components/monitoring-page";

describe("MonitoringPage", () => {
  const metrics = [
    { label: "Uptime", value: 99.99, display: "99.99%", icon: "⬆️" },
    { label: "Latency", value: 45, display: "45ms", icon: "⚡" },
  ];
  it("renders monitoring", () => {
    const { container } = render(
      <MonitoringPage appName="SuperApp" health="healthy" healthIcon="🟢"
        metrics={metrics} activeAlerts={[]} checkedAt="2026-01-01T12:00:00Z" />
    );
    expect(container.textContent).toContain("SuperApp — Monitoring");
    expect(container.textContent).toContain("99.99%");
    expect(container.textContent).toContain("45ms");
    expect(container.textContent).toContain("healthy");
  });
});
