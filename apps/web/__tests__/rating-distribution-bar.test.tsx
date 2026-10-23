import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RatingDistributionBar } from "@/components/rating-distribution-bar";

describe("RatingDistributionBar", () => {
  it("renders", () => {
    const bars = [
      { stars: 5, count: 50, pct: 50 }, { stars: 4, count: 30, pct: 30 },
      { stars: 3, count: 10, pct: 10 }, { stars: 2, count: 5, pct: 5 },
      { stars: 1, count: 5, pct: 5 },
    ];
    const { container } = render(<RatingDistributionBar bars={bars} avg={4.2} total={100} />);
    expect(container.textContent).toContain("4.2");
    expect(container.textContent).toContain("100");
    expect(container.textContent).toContain("50");
  });
});
