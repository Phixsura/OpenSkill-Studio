import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RatingBreakdownChart } from "@/components/rating-breakdown-chart";

describe("RatingBreakdownChart", () => {
  it("renders", () => {
    const dist = { 5: 30, 4: 20, 3: 10, 2: 5, 1: 2 };
    const { container } = render(
      <RatingBreakdownChart avg={4.4} total={67} distribution={dist} trend="improving" fiveStarPct={44.8} />
    );
    expect(container.textContent).toContain("4.4");
    expect(container.textContent).toContain("67 ratings");
    expect(container.textContent).toContain("44.8% five-star");
    expect(container.textContent).toContain("📈");
    expect(container.textContent).toContain("30");
  });
});
