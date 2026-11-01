import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ExtensionHealthPanel } from "@/components/extension-health-panel";

const mockMetrics = {
  extensionId: "ext-1",
  status: "healthy" as const,
  uptime: 99.9,
  avgResponseMs: 45,
  errorRate: 0.2,
  lastCheck: "30s ago",
  incidents: [
    { id: "i1", message: "High latency spike", severity: "warning", timestamp: "2h ago" },
    { id: "i2", message: "Connection timeout", severity: "critical", timestamp: "1d ago" },
  ],
};

describe("ExtensionHealthPanel", () => {
  it("renders health status", () => {
    const { container } = render(<ExtensionHealthPanel metrics={mockMetrics} />);
    expect(container.textContent).toContain("Healthy");
    expect(container.textContent).toContain("99.9%");
    expect(container.textContent).toContain("45ms");
    expect(container.textContent).toContain("0.2%");
  });

  it("renders incidents", () => {
    const { container } = render(<ExtensionHealthPanel metrics={mockMetrics} />);
    expect(container.textContent).toContain("High latency spike");
    expect(container.textContent).toContain("Connection timeout");
  });

  it("renders degraded status", () => {
    const degraded = { ...mockMetrics, status: "degraded" as const };
    const { container } = render(<ExtensionHealthPanel metrics={degraded} />);
    expect(container.textContent).toContain("Degraded");
  });
});
