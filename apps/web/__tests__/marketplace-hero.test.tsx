import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MarketplaceHero } from "@/components/marketplace-hero";

describe("MarketplaceHero", () => {
  it("shows tagline", () => {
    const { container } = render(<MarketplaceHero tagline="Build amazing apps" totalApps={100} totalDevelopers={20} />);
    expect(container.textContent).toContain("Build amazing apps");
    expect(container.textContent).toContain("100 apps");
  });
  it("has CTAs", () => {
    const { container } = render(<MarketplaceHero tagline="X" totalApps={0} totalDevelopers={0} />);
    expect(container.textContent).toContain("Explore Apps");
    expect(container.textContent).toContain("Build an App");
  });
});
