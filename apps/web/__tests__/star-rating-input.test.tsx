import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { StarRatingInput } from "@/components/star-rating-input";

describe("StarRatingInput", () => {
  const labels = { 1: "Poor", 2: "Fair", 3: "Good", 4: "Very Good", 5: "Excellent" };
  it("renders", () => {
    const { container } = render(
      <StarRatingInput maxStars={5} value={3} labels={labels} onChange={vi.fn()} />
    );
    expect(container.querySelectorAll("button").length).toBe(5);
    expect(container.textContent).toContain("Good");
  });
  it("click star", () => {
    const fn = vi.fn();
    const { container } = render(
      <StarRatingInput maxStars={5} value={0} labels={labels} onChange={fn} />
    );
    fireEvent.click(container.querySelectorAll("button")[3]); // 4th star
    expect(fn).toHaveBeenCalledWith(4);
  });
});
