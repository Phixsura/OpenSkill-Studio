import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { MarketplaceSearchBar } from "@/components/marketplace-search-bar";

describe("MarketplaceSearchBar", () => {
  it("renders search bar", () => {
    const { container } = render(
      <MarketplaceSearchBar recentSearches={["webhook"]} popularSearches={["code editor"]} onSearch={vi.fn()} />
    );
    expect(container.querySelector("input")).toBeTruthy();
    expect(container.textContent).toContain("Search");
  });
});
