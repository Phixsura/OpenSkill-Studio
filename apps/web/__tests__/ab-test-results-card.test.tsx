import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ABTestResultsCard } from "@/components/ab-test-results-card";

describe("ABTestResultsCard", () => {
  it("renders winner", () => {
    const { container } = render(
      <ABTestResultsCard testName="Checkout v2"
        control={{ visitors: 5000, conversions: 200, rate: 4.0, rateDisplay: "4.00%" }}
        variant={{ visitors: 5000, conversions: 280, rate: 5.6, rateDisplay: "5.60%" }}
        liftDisplay="+40.0%" significant={true} winner="variant" />
    );
    expect(container.textContent).toContain("Checkout v2");
    expect(container.textContent).toContain("4.00%");
    expect(container.textContent).toContain("5.60%");
    expect(container.textContent).toContain("Winner");
    expect(container.textContent).toContain("Significant");
  });
});
