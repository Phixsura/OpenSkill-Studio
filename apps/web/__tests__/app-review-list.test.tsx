import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AppReviewList } from "@/components/app-review-list";

describe("AppReviewList", () => {
  it("renders reviews", () => {
    const { container } = render(
      <AppReviewList summary={{ count: 3, avgDisplay: "4.0 ⭐", distribution: { 5: 1, 4: 1, 3: 1, 2: 0, 1: 0 } }}
        reviews={[
          { userId: "u1", rating: 5, title: "Amazing", body: "Love it" },
          { userId: "u2", rating: 4, title: "Good", body: "" },
        ]} />
    );
    expect(container.textContent).toContain("Reviews");
    expect(container.textContent).toContain("4.0 ⭐");
    expect(container.textContent).toContain("3 reviews");
    expect(container.textContent).toContain("Amazing");
    expect(container.textContent).toContain("Love it");
  });
});
