import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SearchFilterSidebar } from "@/components/search-filter-sidebar";

describe("SearchFilterSidebar", () => {
  const filters = {
    category: { label: "Category", type: "select", options: ["connector", "analytics"] },
    verified: { label: "Verified", type: "boolean" },
  };
  it("renders filters", () => {
    const { container } = render(<SearchFilterSidebar filters={filters} activeFilters={{}} onFilter={vi.fn()} onClear={vi.fn()} />);
    expect(container.textContent).toContain("Category");
    expect(container.textContent).toContain("Verified");
    expect(container.querySelector("select")).toBeTruthy();
  });
  it("shows clear button", () => {
    const fn = vi.fn();
    const { container } = render(<SearchFilterSidebar filters={filters} activeFilters={{ category: "connector" }} onFilter={vi.fn()} onClear={fn} />);
    expect(container.textContent).toContain("Clear (1)");
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent?.includes("Clear"))!);
    expect(fn).toHaveBeenCalled();
  });
});
