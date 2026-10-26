import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { MarketplaceSearchBar } from "@/components/marketplace-search-bar";

const results = [{ extensionId: "e1", name: "Auth Plugin", description: "Auth helper", installs: 100, rating: 4, tags: ["auth"] }];

describe("MarketplaceSearchBar", () => {
  it("renders search and results", () => {
    const { container } = render(<MarketplaceSearchBar results={results} />);
    expect(container.querySelector("input")).toBeTruthy();
    expect(container.textContent).toContain("Auth Plugin");
    expect(container.textContent).toContain("100 installs");
  });
  it("triggers search", () => {
    const fn = vi.fn();
    const { container } = render(<MarketplaceSearchBar results={[]} onSearch={fn} />);
    const input = container.querySelector("input")!;
    fireEvent.change(input, { target: { value: "test" } });
    fireEvent.click(container.querySelector("button")!);
    expect(fn).toHaveBeenCalledWith("test");
  });
});
