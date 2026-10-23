import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RatePlanCard } from "@/components/rate-plan-card";

describe("RatePlanCard", () => {
  it("renders plan details", () => {
    const { container } = render(
      <RatePlanCard planId="pro" rpm={1000} rpd={100000} burst={100} concurrent={50}
        rpmUsagePct={50} rpdUsagePct={30} throttled={false} upgradeSuggested={false} />
    );
    expect(container.textContent).toContain("pro Plan");
    expect(container.textContent).toContain("1000");
    expect(container.textContent).toContain("100,000");
    expect(container.textContent).toContain("50%");
  });
  it("shows throttled", () => {
    const { container } = render(
      <RatePlanCard planId="free" rpm={60} rpd={1000} burst={10} concurrent={5}
        rpmUsagePct={100} rpdUsagePct={50} throttled={true} upgradeSuggested={true} />
    );
    expect(container.textContent).toContain("Throttled");
  });
});
