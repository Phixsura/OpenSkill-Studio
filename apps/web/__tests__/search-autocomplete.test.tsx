import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SearchAutocomplete } from "@/components/search-autocomplete";

describe("SearchAutocomplete", () => {
  it("renders", () => {
    const { container } = render(
      <SearchAutocomplete onSearch={vi.fn()} suggestions={[]} onSelect={vi.fn()} placeholder="Search..." />
    );
    expect(container.querySelector("input")).toBeTruthy();
    expect(container.querySelector("input")?.getAttribute("placeholder")).toBe("Search...");
  });
});
