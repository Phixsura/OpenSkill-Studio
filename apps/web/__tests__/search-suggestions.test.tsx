import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SearchSuggestions } from "@/components/search-suggestions";

describe("SearchSuggestions", () => {
  it("renders suggestions", () => {
    const onSelect = vi.fn();
    const { container, getByText } = render(
      <SearchSuggestions showTrending={false} onSelect={onSelect}
        suggestions={["slack integration", "slack bot"]}
        trending={[]} />
    );
    expect(container.textContent).toContain("slack integration");
    fireEvent.click(getByText("slack integration"));
    expect(onSelect).toHaveBeenCalledWith("slack integration");
  });

  it("renders trending", () => {
    const { container } = render(
      <SearchSuggestions showTrending={true} onSelect={vi.fn()}
        suggestions={[]}
        trending={[{ query: "analytics", trend: "🔥" }]} />
    );
    expect(container.textContent).toContain("Trending");
    expect(container.textContent).toContain("analytics");
  });
});
