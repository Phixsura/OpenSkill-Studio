import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { GwCircuitStatsPanel } from "@/components/gw-circuit-stats-panel";
describe("GwCircuitStatsPanel", () => {
  it("renders", () => {
    const { container } = render(
      <GwCircuitStatsPanel totalTrips={3} totalBlocked={10}
        backends={[
          { backend: "api", trips: 2, recoveries: 1, requestsBlocked: 8 },
          { backend: "db", trips: 1, recoveries: 0, requestsBlocked: 2 },
        ]} />
    );
    expect(container.textContent).toContain("Gateway Circuits");
    expect(container.textContent).toContain("3 trips");
    expect(container.textContent).toContain("10 blocked");
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("2 trips");
    expect(container.textContent).toContain("8 blocked");
  });
});
