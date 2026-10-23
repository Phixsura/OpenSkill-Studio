import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { HeroSection } from "@/components/hero-section";

describe("HeroSection", () => {
  it("renders", () => {
    const { container } = render(
      <HeroSection headline="Build Apps" subheadline="The platform" ctaPrimary="Start"
        ctaSecondary="Learn More" stats={[{ label: "Apps", value: "500+" }]}
        gradient="from-blue-600 to-purple-600" onCtaPrimary={vi.fn()} onCtaSecondary={vi.fn()} />
    );
    expect(container.textContent).toContain("Build Apps");
    expect(container.textContent).toContain("The platform");
    expect(container.textContent).toContain("Start");
    expect(container.textContent).toContain("Learn More");
    expect(container.textContent).toContain("500+");
  });
  it("primary cta", () => {
    const fn = vi.fn();
    const { container } = render(
      <HeroSection headline="X" subheadline="Y" ctaPrimary="Go" ctaSecondary={null}
        stats={[]} gradient="from-blue-600 to-purple-600" onCtaPrimary={fn} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Go")!);
    expect(fn).toHaveBeenCalled();
  });
});
