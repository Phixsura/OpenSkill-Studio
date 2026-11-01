import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ReviewSummaryCard } from "@/components/review-summary-card";

describe("ReviewSummaryCard", () => {
  it("renders", () => {
    const dist = { 5: 20, 4: 15, 3: 5, 2: 3, 1: 2 };
    const { container } = render(
      <ReviewSummaryCard avgRating={4.2} total={45} distribution={dist}
        sentiment="positive" positivePct={77.8} />
    );
    expect(container.textContent).toContain("4.2");
    expect(container.textContent).toContain("45 reviews");
    expect(container.textContent).toContain("😊");
    expect(container.textContent).toContain("77.8% positive");
    expect(container.textContent).toContain("20");
  });
});
