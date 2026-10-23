import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SearchBarAutocomplete } from "@/components/search-bar-autocomplete";

describe("SearchBarAutocomplete", () => {
  it("renders search bar", () => {
    const { container } = render(
      <SearchBarAutocomplete onSearch={vi.fn(() => ({ sections: {}, total: 0 }))} onSelect={vi.fn()} />
    );
    expect(container.querySelector("input")).toBeTruthy();
  });
});
