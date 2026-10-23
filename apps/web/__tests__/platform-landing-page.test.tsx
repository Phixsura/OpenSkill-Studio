import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { PlatformLandingPage } from "@/components/platform-landing-page";

describe("PlatformLandingPage", () => {
  const props = {
    headline: "Build, Ship, Scale",
    subheadline: "The complete platform",
    statsBar: [{ label: "Apps", value: "500+" }],
    features: [{ title: "Easy SDK", description: "Get started fast", icon: "🚀" }],
    testimonials: [{ quote: "Amazing!", author: "Alice", role: "CTO" }],
    footerLinks: [{ section: "Product", links: ["Marketplace", "API"] }],
  };
  it("renders complete landing page", () => {
    const { container } = render(<PlatformLandingPage {...props} onCta={vi.fn()} />);
    expect(container.textContent).toContain("Build, Ship, Scale");
    expect(container.textContent).toContain("500+");
    expect(container.textContent).toContain("Get Started Free");
    expect(container.textContent).toContain("🚀");
    expect(container.textContent).toContain("Easy SDK");
    expect(container.textContent).toContain("Amazing!");
    expect(container.textContent).toContain("Alice");
    expect(container.textContent).toContain("Product");
    expect(container.textContent).toContain("© 2026");
  });
  it("cta click", () => {
    const fn = vi.fn();
    const { container } = render(<PlatformLandingPage {...props} onCta={fn} />);
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Get Started Free")!);
    expect(fn).toHaveBeenCalledWith("signup");
  });
});
