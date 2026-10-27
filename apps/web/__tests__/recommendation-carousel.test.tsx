import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { RecommendationCarousel } from "@/components/recommendation-carousel";

const recs = [
  { extensionId: "e1", name: "Auth Plugin", category: "security", installs: 500, rating: 4 },
  { extensionId: "e2", name: "Charts", category: "ui", installs: 300, rating: 5 },
];

describe("RecommendationCarousel", () => {
  it("renders recommendations", () => {
    const { container } = render(<RecommendationCarousel recommendations={recs} title="Recommended" />);
    expect(container.textContent).toContain("Recommended");
    expect(container.textContent).toContain("Auth Plugin");
    expect(container.textContent).toContain("Charts");
  });
  it("select extension", () => {
    const fn = vi.fn();
    const { container } = render(<RecommendationCarousel recommendations={recs} title="For You" onSelect={fn} />);
    fireEvent.click(container.querySelectorAll("button")[0]);
    expect(fn).toHaveBeenCalledWith("e1");
  });
});
