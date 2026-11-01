import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TelemetryOverviewDashboard } from "@/components/telemetry-overview-dashboard";

const snapshot = {
  metrics: { requests: 50000, errors: 250, errorRate: 0.5, avgLatency: 45, p99Latency: 200 },
  resources: { cpu: 65, memoryMb: 512 },
  signals: { traces: 100, slowTraces: 5, logErrors: 20, logWarns: 50 },
  health: { score: 92, alerts: 1 },
};

describe("TelemetryOverviewDashboard", () => {
  it("renders full telemetry dashboard", () => {
    const { container } = render(<TelemetryOverviewDashboard snapshot={snapshot} extensionName="Slack Bot" />);
    expect(container.textContent).toContain("Slack Bot");
    expect(container.textContent).toContain("92");
    expect(container.textContent).toContain("50,000");
    expect(container.textContent).toContain("0.5%");
    expect(container.textContent).toContain("200ms");
    expect(container.textContent).toContain("65%");
    expect(container.textContent).toContain("1 alerts");
  });
});
