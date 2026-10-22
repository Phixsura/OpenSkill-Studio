import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MarketplaceNav } from "@/components/marketplace-nav";

describe("MarketplaceNav", () => {
  it("shows all nav items", () => {
    const { container } = render(<MarketplaceNav activePage="home" />);
    expect(container.textContent).toContain("Home");
    expect(container.textContent).toContain("All Apps");
    expect(container.textContent).toContain("Trending");
  });
  it("highlights active", () => {
    const { container } = render(<MarketplaceNav activePage="trending" />);
    const active = container.querySelector("[class*='border-blue']");
    expect(active?.textContent).toContain("Trending");
  });
  it("has 6 links", () => {
    const { container } = render(<MarketplaceNav activePage="" />);
    expect(container.querySelectorAll("a").length).toBe(6);
  });
});
