import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SearchFilterBar } from "@/components/search-filter-bar";

describe("SearchFilterBar", () => {
  it("renders filters", () => {
    const onRemove = vi.fn();
    const onClear = vi.fn();
    const { container, getByText } = render(
      <SearchFilterBar activeCount={2} onRemove={onRemove} onClear={onClear}
        filters={[
          { key: "categories", display: "tools" },
          { key: "rating_min", display: "≥ 4⭐" },
        ]} />
    );
    expect(container.textContent).toContain("2 filters");
    expect(container.textContent).toContain("tools");
    expect(container.textContent).toContain("≥ 4⭐");
    fireEvent.click(getByText("Clear all"));
    expect(onClear).toHaveBeenCalled();
  });
});
