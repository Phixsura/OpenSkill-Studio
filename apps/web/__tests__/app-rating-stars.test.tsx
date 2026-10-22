import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AppRatingStars } from "@/components/app-rating-stars";

describe("AppRatingStars", () => {
  it("shows 5 stars for 5.0", () => {
    const { container } = render(<AppRatingStars rating={5.0} count={10} />);
    expect(container.textContent).toContain("★★★★★");
  });

  it("shows count", () => {
    const { container } = render(<AppRatingStars rating={4.0} count={42} />);
    expect(container.textContent).toContain("(42)");
  });

  it("shows half star", () => {
    const { container } = render(<AppRatingStars rating={3.5} count={5} />);
    expect(container.textContent).toContain("½");
  });

  it("shows empty stars", () => {
    const { container } = render(<AppRatingStars rating={2.0} count={1} />);
    expect(container.textContent).toContain("☆");
  });
});
