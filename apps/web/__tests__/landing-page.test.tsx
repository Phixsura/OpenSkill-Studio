import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { LandingPage } from "@/components/landing-page";

describe("LandingPage", () => {
  it("renders landing page", () => {
    const { container } = render(
      <LandingPage heroTitle="Build Apps" heroSubtitle="The platform"
        ctaPrimary={{ label: "Start", href: "/signup" }}
        ctaSecondary={{ label: "Docs", href: "/docs" }}
        features={[{ icon: "📦", title: "Marketplace", description: "Publish apps" }]}
        stats={[{ value: "5K+", label: "Apps" }]}
        testimonials={[{ quote: "Great!", author: "Alice", role: "CTO" }]} />
    );
    expect(container.textContent).toContain("Build Apps");
    expect(container.textContent).toContain("Start");
    expect(container.textContent).toContain("Marketplace");
    expect(container.textContent).toContain("5K+");
    expect(container.textContent).toContain("Great!");
    expect(container.textContent).toContain("Alice");
  });
});
