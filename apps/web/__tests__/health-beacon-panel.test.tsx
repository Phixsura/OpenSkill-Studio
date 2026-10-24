import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { HealthBeaconPanel } from "@/components/health-beacon-panel";

describe("HealthBeaconPanel", () => {
  it("renders beacons", () => {
    const { container } = render(
      <HealthBeaconPanel uniqueServices={5} healthyPct={80} allHealthy={false}
        byStatus={{ healthy: 4, degraded: 1 }} staleServices={["old-service"]} />
    );
    expect(container.textContent).toContain("Health Beacons");
    expect(container.textContent).toContain("5 services");
    expect(container.textContent).toContain("80% healthy");
    expect(container.textContent).toContain("4");
    expect(container.textContent).toContain("healthy");
    expect(container.textContent).toContain("Stale: old-service");
  });
});
