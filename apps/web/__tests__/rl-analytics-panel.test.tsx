import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RlAnalyticsPanel } from "@/components/rl-analytics-panel";
describe("RlAnalyticsPanel", () => {
  it("renders", () => {
    const { container } = render(
      <RlAnalyticsPanel totalAllowed={8000} totalDenied={2000} overallDenyRate={20}
        tenants={[
          { tenantId: "t2", allowed: 0, denied: 1500, denyRate: 100 },
          { tenantId: "t1", allowed: 8000, denied: 500, denyRate: 5.9 },
        ]} />
    );
    expect(container.textContent).toContain("Rate Limit Analytics");
    expect(container.textContent).toContain("8,000 allowed");
    expect(container.textContent).toContain("2,000 denied");
    expect(container.textContent).toContain("20%");
    expect(container.textContent).toContain("t2");
    expect(container.textContent).toContain("100%");
  });
});
