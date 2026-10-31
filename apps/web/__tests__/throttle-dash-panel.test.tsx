import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ThrottleDashPanel } from "@/components/throttle-dash-panel";
describe("ThrottleDashPanel", () => {
  it("renders", () => {
    const { container } = render(
      <ThrottleDashPanel totalAllowed={8000} totalThrottled={2000} overallRate={20}
        tenants={[
          { tenantId: "t2", allowed: 0, throttled: 1500, throttleRate: 100 },
          { tenantId: "t1", allowed: 8000, throttled: 500, throttleRate: 5.9 },
        ]} />
    );
    expect(container.textContent).toContain("Throttle Dashboard");
    expect(container.textContent).toContain("8,000 allowed");
    expect(container.textContent).toContain("2,000 throttled");
    expect(container.textContent).toContain("20%");
    expect(container.textContent).toContain("t2");
    expect(container.textContent).toContain("100%");
  });
});
