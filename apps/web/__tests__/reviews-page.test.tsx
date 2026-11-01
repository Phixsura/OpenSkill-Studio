import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ReviewsPage } from "@/components/reviews-page";

describe("ReviewsPage", () => {
  const reviews = [
    { id: "r1", rating: 5, title: "Great!", body: "Love it", author: "Alice", helpfulCount: 10, hasResponse: true },
  ];
  it("renders reviews page", () => {
    const { container } = render(
      <ReviewsPage appName="SuperApp" reviews={reviews} total={1} avgRating={5.0}
        stars="★★★★★" distribution={{ 1: 0, 2: 0, 3: 0, 4: 0, 5: 1 }}
        sortBy="newest" onSort={vi.fn()} onFilterRating={vi.fn()} />
    );
    expect(container.textContent).toContain("SuperApp Reviews");
    expect(container.textContent).toContain("Great!");
    expect(container.textContent).toContain("by Alice");
    expect(container.textContent).toContain("Response");
    expect(container.textContent).toContain("★★★★★");
  });
});
