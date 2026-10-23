import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SearchBar } from "@/components/search-bar";

describe("SearchBar", () => {
  it("renders", () => {
    const { container } = render(
      <SearchBar placeholder="Search apps..." shortcut="⌘K" debounceMs={300} onSearch={vi.fn()} />
    );
    expect(container.querySelector("input")).toBeTruthy();
    expect(container.querySelector("input")?.getAttribute("placeholder")).toBe("Search apps...");
    expect(container.textContent).toContain("⌘K");
    expect(container.textContent).toContain("🔍");
  });
});
