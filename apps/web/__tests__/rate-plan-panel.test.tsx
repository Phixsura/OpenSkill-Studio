import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RatePlanPanel } from "@/components/rate-plan-panel";
describe("RatePlanPanel", () => {
  it("renders", () => {
    const { container } = render(
      <RatePlanPanel plan="free" dailyPct={90} monthlyPct={50}
        exceeded={false} recommendUpgrade={true} rpm={60} />
    );
    expect(container.textContent).toContain("Rate Plan");
    expect(container.textContent).toContain("free");
    expect(container.textContent).toContain("60 rpm");
    expect(container.textContent).toContain("90%");
    expect(container.textContent).toContain("50%");
    expect(container.textContent).toContain("upgrading");
  });
});
