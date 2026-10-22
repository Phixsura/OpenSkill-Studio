import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SearchSuggestions } from "@/components/search-suggestions";

describe("SearchSuggestions", () => {
  it("shows suggestions", () => {
    const { container } = render(<SearchSuggestions suggestions={["App A", "App B"]} onSelect={vi.fn()} visible={true} />);
    expect(container.textContent).toContain("App A");
  });
  it("hidden when not visible", () => {
    const { container } = render(<SearchSuggestions suggestions={["X"]} onSelect={vi.fn()} visible={false} />);
    expect(container.innerHTML).toBe("");
  });
  it("calls onSelect", () => {
    const onSelect = vi.fn();
    const { container } = render(<SearchSuggestions suggestions={["Pick Me"]} onSelect={onSelect} visible={true} />);
    fireEvent.click(container.querySelector("button")!);
    expect(onSelect).toHaveBeenCalledWith("Pick Me");
  });
});
