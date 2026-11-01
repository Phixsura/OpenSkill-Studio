import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { FinalHeroPage } from "@/components/final-hero-page";

describe("FinalHeroPage", () => {
  it("renders hero", () => {
    const onPrimary = vi.fn();
    const { container, getByText } = render(
      <FinalHeroPage headline="Build Amazing Apps" subheadline="The platform"
        ctaPrimary="Start" ctaSecondary="Docs"
        trustRating="4.8 ⭐" trustInstalls="2.5M+"
        stats={[{ label: "Apps", value: "500+", icon: "📱" }]}
        features={[{ title: "Marketplace", description: "Find apps", icon: "🏪" }]}
        onPrimary={onPrimary} onSecondary={vi.fn()} />
    );
    expect(container.textContent).toContain("Build Amazing Apps");
    expect(container.textContent).toContain("500+");
    expect(container.textContent).toContain("Marketplace");
    expect(container.textContent).toContain("4.8 ⭐");
    fireEvent.click(getByText("Start"));
    expect(onPrimary).toHaveBeenCalled();
  });
});
