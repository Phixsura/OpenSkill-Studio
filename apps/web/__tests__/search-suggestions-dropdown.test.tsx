import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SearchSuggestionsDropdown } from "@/components/search-suggestions-dropdown";

describe("SearchSuggestionsDropdown", () => {
  const suggestions = [
    { type: "app", text: "Slack Bot", icon: "📦" },
    { type: "category", text: "Connectors", icon: "📂" },
  ];
  it("renders when visible", () => {
    const { container } = render(<SearchSuggestionsDropdown suggestions={suggestions} onSelect={vi.fn()} visible={true} />);
    expect(container.textContent).toContain("Slack Bot");
    expect(container.textContent).toContain("Connectors");
  });
  it("hidden when not visible", () => {
    const { container } = render(<SearchSuggestionsDropdown suggestions={suggestions} onSelect={vi.fn()} visible={false} />);
    expect(container.innerHTML).toBe("");
  });
  it("selects suggestion", () => {
    const fn = vi.fn();
    const { container } = render(<SearchSuggestionsDropdown suggestions={suggestions} onSelect={fn} visible={true} />);
    fireEvent.click(container.querySelectorAll("button")[0]);
    expect(fn).toHaveBeenCalledWith("Slack Bot");
  });
});
