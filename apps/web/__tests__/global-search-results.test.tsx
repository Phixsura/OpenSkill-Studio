import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { GlobalSearchResults } from "@/components/global-search-results";

describe("GlobalSearchResults", () => {
  const results = [
    { id: "a1", title: "Auth SDK", category: "apps", snippet: "auth sdk" },
    { id: "d1", title: "Auth Guide", category: "docs", snippet: "auth guide" },
  ];
  it("renders", () => {
    const { container } = render(
      <GlobalSearchResults results={results} query="auth" total={2}
        byCategory={{ apps: 1, docs: 1 }} onSelect={vi.fn()} />
    );
    expect(container.textContent).toContain('2 results for');
    expect(container.textContent).toContain("Auth SDK");
    expect(container.textContent).toContain("Auth Guide");
    expect(container.textContent).toContain("📦");
    expect(container.textContent).toContain("📚");
  });
  it("select", () => {
    const fn = vi.fn();
    const { container } = render(
      <GlobalSearchResults results={results} query="auth" total={2}
        byCategory={{}} onSelect={fn} />
    );
    fireEvent.click(container.querySelectorAll("button")[0]);
    expect(fn).toHaveBeenCalledWith("a1", "apps");
  });
});
