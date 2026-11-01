import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SearchFilters } from "@/components/search-filters";

describe("SearchFilters", () => {
  const facets = { category: [{ value: "tools", count: 5 }, { value: "games", count: 3 }] };
  it("renders facets", () => {
    const { container } = render(
      <SearchFilters facets={facets} activeFilters={{}} onFilter={vi.fn()} onClear={vi.fn()} />
    );
    expect(container.textContent).toContain("tools");
    expect(container.textContent).toContain("5");
    expect(container.textContent).toContain("games");
  });
  it("filter click", () => {
    const fn = vi.fn();
    const { container } = render(
      <SearchFilters facets={facets} activeFilters={{}} onFilter={fn} onClear={vi.fn()} />
    );
    fireEvent.click(container.querySelectorAll("button")[0]);
    expect(fn).toHaveBeenCalledWith("category", "tools");
  });
});
