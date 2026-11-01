import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { HeroSection } from "@/components/hero-section";

describe("HeroSection", () => {
  it("renders hero", () => {
    const { container } = render(
      <HeroSection title="Build faster" subtitle="The platform" badge="New v3"
        ctaPrimary={{ label: "Start", href: "/go" }} ctaSecondary={{ label: "Docs", href: "/docs" }}
        stats={[{ value: "5K+", label: "Apps" }]} />
    );
    expect(container.textContent).toContain("Build faster");
    expect(container.textContent).toContain("The platform");
    expect(container.textContent).toContain("New v3");
    expect(container.textContent).toContain("Start");
    expect(container.textContent).toContain("Docs");
    expect(container.textContent).toContain("5K+");
  });
});
