import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { PortalSearchBar } from "@/components/portal-search-bar";

describe("PortalSearchBar", () => {
  it("has search input", () => {
    const { container } = render(<PortalSearchBar onSearch={vi.fn()} results={[]} />);
    expect(container.querySelector("input")).toBeTruthy();
  });
  it("has placeholder", () => {
    const { container } = render(<PortalSearchBar onSearch={vi.fn()} results={[]} />);
    expect(container.querySelector("input")?.placeholder).toContain("Search");
  });
});
