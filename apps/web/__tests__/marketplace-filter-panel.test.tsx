import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { MarketplaceFilterPanel } from "@/components/marketplace-filter-panel";

describe("MarketplaceFilterPanel", () => {
  it("shows category select", () => {
    const { container } = render(<MarketplaceFilterPanel categories={["connector"]} selectedCategory="" onCategoryChange={vi.fn()} verifiedOnly={false} onVerifiedChange={vi.fn()} minHealth={0} onMinHealthChange={vi.fn()} />);
    expect(container.querySelector("select")).toBeTruthy();
  });
  it("shows health slider", () => {
    const { container } = render(<MarketplaceFilterPanel categories={[]} selectedCategory="" onCategoryChange={vi.fn()} verifiedOnly={false} onVerifiedChange={vi.fn()} minHealth={80} onMinHealthChange={vi.fn()} />);
    expect(container.textContent).toContain("80");
  });
  it("shows verified checkbox", () => {
    const { container } = render(<MarketplaceFilterPanel categories={[]} selectedCategory="" onCategoryChange={vi.fn()} verifiedOnly={false} onVerifiedChange={vi.fn()} minHealth={0} onMinHealthChange={vi.fn()} />);
    expect(container.querySelector("input[type='checkbox']")).toBeTruthy();
  });
});
