import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CapacityHeadroomPanel } from "@/components/capacity-headroom-panel";
describe("CapacityHeadroomPanel", () => {
  it("renders", () => {
    const { container } = render(
      <CapacityHeadroomPanel bottleneck="api" minHeadroomPct={20}
        services={[
          { service: "api", currentRps: 800, maxRps: 1000, headroomPct: 20, status: "warning" },
          { service: "worker", currentRps: 200, maxRps: 500, headroomPct: 60, status: "ok" },
        ]} />
    );
    expect(container.textContent).toContain("Capacity Headroom");
    expect(container.textContent).toContain("min: 20%");
    expect(container.textContent).toContain("bottleneck: api");
    expect(container.textContent).toContain("800/1000 rps");
    expect(container.textContent).toContain("20% free");
  });
});
