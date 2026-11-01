import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { HealthCheckStatusGrid } from "@/components/health-check-status-grid";

describe("HealthCheckStatusGrid", () => {
  const checks = [
    { url: "/health", status_code: 200, latency_ms: 30, healthy: true },
    { url: "/api", status_code: 503, latency_ms: 5100, healthy: false },
  ];
  it("renders", () => {
    const { container } = render(
      <HealthCheckStatusGrid checks={checks} allHealthy={false} avgLatencyMs={2565} />
    );
    expect(container.textContent).toContain("Health Checks");
    expect(container.textContent).toContain("/health");
    expect(container.textContent).toContain("200");
    expect(container.textContent).toContain("/api");
    expect(container.textContent).toContain("503");
    expect(container.textContent).toContain("2565ms avg");
  });
});
