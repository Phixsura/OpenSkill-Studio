import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { RatingSystemPanel } from "@/components/rating-system-panel";

const stats = {
  count: 150, average: 4.3, bayesian: 4.1,
  distribution: { 1: 5, 2: 10, 3: 20, 4: 45, 5: 70 },
  verifiedCount: 80,
};

describe("RatingSystemPanel", () => {
  it("renders rating stats", () => {
    const { container } = render(<RatingSystemPanel stats={stats} />);
    expect(container.textContent).toContain("4.3");
    expect(container.textContent).toContain("150 ratings");
  });
  it("calls onRate", () => {
    const fn = vi.fn();
    const { container } = render(<RatingSystemPanel stats={stats} onRate={fn} />);
    const stars = container.querySelectorAll("button");
    fireEvent.click(stars[4]); // 5 stars
    expect(fn).toHaveBeenCalledWith(5);
  });
});
