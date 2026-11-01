import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ReviewList } from "@/components/review-list";

describe("ReviewList", () => {
  const reviews = [{ id: "r1", rating: 5, title: "Amazing!", body: "Best app ever", createdAt: "2026-01-01" }];
  const distribution = { 1: 0, 2: 0, 3: 0, 4: 0, 5: 1 };
  it("renders reviews", () => {
    const { container } = render(
      <ReviewList reviews={reviews} avgRating={5.0} total={1} starsDisplay="★★★★★" distribution={distribution} />
    );
    expect(container.textContent).toContain("5");
    expect(container.textContent).toContain("★★★★★");
    expect(container.textContent).toContain("Amazing!");
    expect(container.textContent).toContain("Best app ever");
  });
});
