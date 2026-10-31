import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { LandingPageSections } from "@/components/landing-page-sections";

describe("LandingPageSections", () => {
  it("renders sections", () => {
    const onStart = vi.fn();
    const { container, getByText } = render(
      <LandingPageSections pricingTitle="Start Free" pricingSubtitle="No CC"
        onGetStarted={onStart}
        features={[{ icon: "🏪", title: "Marketplace", desc: "500+ apps" }]}
        testimonials={[{ quote: "Amazing!", author: "Dev", rating: 5 }]} />
    );
    expect(container.textContent).toContain("Everything You Need");
    expect(container.textContent).toContain("Marketplace");
    expect(container.textContent).toContain("Amazing!");
    expect(container.textContent).toContain("Start Free");
    fireEvent.click(getByText("Get Started Free"));
    expect(onStart).toHaveBeenCalled();
  });
});
