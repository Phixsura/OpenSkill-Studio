import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RatingSummary } from "@/components/rating-summary";

describe("RatingSummary", () => {
  it("renders ratings", () => {
    const { container } = render(
      <RatingSummary average={4.1} averageDisplay="4.1 ⭐" count={10} sentiment="positive"
        distribution={{ 5: 4, 4: 4, 3: 1, 2: 1, 1: 0 }} />
    );
    expect(container.textContent).toContain("4.1");
    expect(container.textContent).toContain("10 reviews");
    expect(container.textContent).toContain("positive");
  });
});
