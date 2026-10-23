import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { EmptySearchState } from "@/components/empty-search-state";

describe("EmptySearchState", () => {
  it("renders", () => {
    const { container } = render(
      <EmptySearchState query="xyz" title='No results for "xyz"' icon="🔍"
        suggestions={["Try broader keywords"]} popularSearches={["auth", "payments"]}
        onPopularSearch={vi.fn()} onClearSearch={vi.fn()} />
    );
    expect(container.textContent).toContain('No results for "xyz"');
    expect(container.textContent).toContain("🔍");
    expect(container.textContent).toContain("Try broader keywords");
    expect(container.textContent).toContain("auth");
    expect(container.textContent).toContain("payments");
    expect(container.textContent).toContain("Clear search");
  });
  it("popular search click", () => {
    const fn = vi.fn();
    const { container } = render(
      <EmptySearchState query="x" title="X" icon="🔍" suggestions={[]}
        popularSearches={["auth"]} onPopularSearch={fn} onClearSearch={vi.fn()} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "auth")!);
    expect(fn).toHaveBeenCalledWith("auth");
  });
});
