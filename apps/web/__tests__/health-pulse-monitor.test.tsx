import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { HealthPulseMonitor } from "@/components/health-pulse-monitor";

describe("HealthPulseMonitor", () => {
  it("renders", () => {
    const { container } = render(
      <HealthPulseMonitor healthPct={67} allHealthy={false} improving={true}
        pulses={[
          { service: "api", healthy: true, latencyMs: 50 },
          { service: "db", healthy: true, latencyMs: 10 },
          { service: "cache", healthy: false, latencyMs: 5000 },
        ]} />
    );
    expect(container.textContent).toContain("Health Pulse");
    expect(container.textContent).toContain("67%");
  });
});
