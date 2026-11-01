import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RatingDistribution } from "@/components/rating-distribution";

describe("RatingDistribution", () => {
  it("shows average", () => {
    const { container } = render(<RatingDistribution distribution={{ 5: 10, 4: 5, 3: 2, 2: 1, 1: 0 }} average={4.3} count={18} />);
    expect(container.textContent).toContain("4.3");
    expect(container.textContent).toContain("18 reviews");
  });
  it("shows all 5 rows", () => {
    const { container } = render(<RatingDistribution distribution={{ 5: 0, 4: 0, 3: 0, 2: 0, 1: 0 }} average={0} count={0} />);
    expect(container.querySelectorAll("[class*='flex items-center']").length).toBeGreaterThanOrEqual(5);
  });
});
