import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { EpSlaPanel } from "@/components/ep-sla-panel";
describe("EpSlaPanel", () => {
  it("renders", () => {
    const { container } = render(
      <EpSlaPanel compliancePct={50}
        endpoints={[
          { endpoint: "/api/users", compliant: true, availabilityPct: 99.99, p99Ms: 100, errorRatePct: 0.1 },
          { endpoint: "/api/orders", compliant: false, availabilityPct: 98, p99Ms: 800, errorRatePct: 5 },
        ]} />
    );
    expect(container.textContent).toContain("Endpoint SLA");
    expect(container.textContent).toContain("50% compliant");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("99.99%");
    expect(container.textContent).toContain("/api/orders");
    expect(container.textContent).toContain("800ms");
  });
});
