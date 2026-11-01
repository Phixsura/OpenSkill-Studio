import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ExperimentTracker } from "@/components/experiment-tracker";

describe("ExperimentTracker", () => {
  it("renders experiments", () => {
    const { container } = render(
      <ExperimentTracker results={[
        { experiment: "new-checkout", metric: "conversion", control: 3.5, variant: 4.2, liftPct: 20, significant: true, winner: "variant" },
        { experiment: "pricing-test", metric: "revenue", control: 100, variant: 98, liftPct: -2, significant: false, winner: "inconclusive" },
      ]} />
    );
    expect(container.textContent).toContain("Experiments");
    expect(container.textContent).toContain("2 experiments");
    expect(container.textContent).toContain("new-checkout");
    expect(container.textContent).toContain("variant");
    expect(container.textContent).toContain("+20%");
    expect(container.textContent).toContain("inconclusive");
  });
});
