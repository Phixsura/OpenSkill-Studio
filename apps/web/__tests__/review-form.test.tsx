import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ReviewForm } from "@/components/review-form";

describe("ReviewForm", () => {
  it("renders new review form", () => {
    const { container } = render(
      <ReviewForm appName="SuperApp" isEdit={false} currentRating={0}
        currentTitle="" currentBody="" ratingLabels={{ 1: "Bad", 5: "Great" }}
        onSubmit={vi.fn()} />
    );
    expect(container.textContent).toContain("Write Review — SuperApp");
    expect(container.textContent).toContain("Submit Review");
    expect(container.querySelectorAll("button").length).toBeGreaterThanOrEqual(5); // 5 stars + submit
  });
});
