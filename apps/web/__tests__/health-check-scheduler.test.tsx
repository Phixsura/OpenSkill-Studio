import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { HealthCheckScheduler } from "@/components/health-check-scheduler";

describe("HealthCheckScheduler", () => {
  it("renders checks", () => {
    const { container } = render(
      <HealthCheckScheduler allHealthy={false} onAdd={vi.fn()} checks={[
        { name: "API", url: "https://api/health", interval: "1m", healthy: true, latencyMs: 50 },
        { name: "DB", url: "https://db/health", interval: "5m", healthy: false, latencyMs: 3000 },
      ]} />
    );
    expect(container.textContent).toContain("Health Checks");
    expect(container.textContent).toContain("Issues detected");
    expect(container.textContent).toContain("API");
    expect(container.textContent).toContain("50ms");
    expect(container.textContent).toContain("DB");
    expect(container.textContent).toContain("every 5m");
  });
});
