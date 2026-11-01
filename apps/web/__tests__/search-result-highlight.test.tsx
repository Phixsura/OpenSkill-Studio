import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SearchResultHighlight } from "@/components/search-result-highlight";

describe("SearchResultHighlight", () => {
  it("renders", () => {
    const { container } = render(
      <SearchResultHighlight title="Auth SDK" highlightedTitle="<mark>Auth</mark> SDK"
        snippet="Authentication SDK for developers..." matchCount={2} onClick={vi.fn()} />
    );
    expect(container.textContent).toContain("Auth SDK");
    expect(container.textContent).toContain("2 matches");
    expect(container.textContent).toContain("Authentication SDK");
    expect(container.querySelector("mark")).toBeTruthy();
  });
  it("click", () => {
    const fn = vi.fn();
    const { container } = render(
      <SearchResultHighlight title="X" highlightedTitle="X" snippet="Y"
        matchCount={1} onClick={fn} />
    );
    fireEvent.click(container.querySelector("button")!);
    expect(fn).toHaveBeenCalled();
  });
});
