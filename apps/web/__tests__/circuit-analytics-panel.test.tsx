import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CircuitAnalyticsPanel } from "@/components/circuit-analytics-panel";
describe("CircuitAnalyticsPanel", () => {
  it("renders", () => {
    const { container } = render(
      <CircuitAnalyticsPanel totalTrips={5} flapping={1} mttrMs={45000}
        services={[
          { service: "api", trips: 3, recoveries: 2, avgOpenMs: 30000 },
          { service: "db", trips: 2, recoveries: 1, avgOpenMs: 60000 },
        ]} />
    );
    expect(container.textContent).toContain("Circuit Analytics");
    expect(container.textContent).toContain("5 trips");
    expect(container.textContent).toContain("MTTR 45000ms");
    expect(container.textContent).toContain("1 flapping");
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("3 trips");
  });
});
