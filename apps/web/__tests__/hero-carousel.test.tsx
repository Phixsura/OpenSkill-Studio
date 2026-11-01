import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { HeroCarousel } from "@/components/hero-carousel";

const SLIDES = [{ name: "App A", tagline: "Amazing", category: "connector", ctaUrl: "/a" }];

describe("HeroCarousel", () => {
  it("shows slide", () => {
    const { container } = render(<HeroCarousel slides={SLIDES} />);
    expect(container.textContent).toContain("App A");
    expect(container.textContent).toContain("Learn More");
  });
  it("null when empty", () => {
    const { container } = render(<HeroCarousel slides={[]} />);
    expect(container.innerHTML).toBe("");
  });
});
