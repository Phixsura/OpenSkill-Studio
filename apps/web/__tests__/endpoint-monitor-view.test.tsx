import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { EndpointMonitorView } from "@/components/endpoint-monitor-view";

describe("EndpointMonitorView", () => {
  const endpoints = [
    { url: "/health", uptime_pct: 100, avg_latency_ms: 35 },
    { url: "/api/apps", uptime_pct: 98.5, avg_latency_ms: 120 },
  ];
  it("renders", () => {
    const { container } = render(
      <EndpointMonitorView endpoints={endpoints} overallUptime={99.25}
        avgLatencyMs={77} totalChecks={200} periodHours={24} onRefresh={vi.fn()} />
    );
    expect(container.textContent).toContain("Endpoint Monitor");
    expect(container.textContent).toContain("99.25%");
    expect(container.textContent).toContain("77ms");
    expect(container.textContent).toContain("/health");
    expect(container.textContent).toContain("100%");
    expect(container.textContent).toContain("200 checks");
  });
});
