import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { RecommendationCarousel } from "@/components/recommendation-carousel";

describe("RecommendationCarousel", () => {
  const recs = [
    { id: "a1", name: "ToolX", category: "tools", rating: 4.5, reason: "category_match" },
    { id: "a2", name: "DesignY", category: "design", rating: 3.8, reason: "popular" },
  ];
  it("renders", () => {
    const { container } = render(<RecommendationCarousel recommendations={recs} onInstall={vi.fn()} />);
    expect(container.textContent).toContain("Recommended for You");
    expect(container.textContent).toContain("ToolX");
    expect(container.textContent).toContain("Similar to your apps");
    expect(container.textContent).toContain("Popular");
  });
  it("install", () => {
    const fn = vi.fn();
    const { container } = render(<RecommendationCarousel recommendations={recs} onInstall={fn} />);
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Install")!);
    expect(fn).toHaveBeenCalledWith("a1");
  });
});
