import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { LandingHero } from "@/components/landing-hero";

describe("LandingHero", () => {
  it("renders hero", () => {
    const onPrimary = vi.fn();
    const { container, getByText } = render(
      <LandingHero headline="Build Amazing" subheadline="The platform"
        ctaPrimary="Get Started" ctaSecondary="Docs"
        stats={{ apps: "500+" }} socialProof={[{ name: "GitHub", icon: "⭐", value: "5K stars" }]}
        onPrimary={onPrimary} onSecondary={vi.fn()} />
    );
    expect(container.textContent).toContain("Build Amazing");
    expect(container.textContent).toContain("The platform");
    expect(container.textContent).toContain("500+");
    expect(container.textContent).toContain("5K stars");
    fireEvent.click(getByText("Get Started"));
    expect(onPrimary).toHaveBeenCalled();
  });
});
