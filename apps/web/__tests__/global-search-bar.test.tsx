import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { GlobalSearchBar } from "@/components/global-search-bar";

describe("GlobalSearchBar", () => {
  it("renders results", () => {
    const { container } = render(
      <GlobalSearchBar totalMatches={2} onSearch={vi.fn()}
        byType={{ app: 1, document: 1 }}
        results={[
          { name: "Auth Service", type: "app", description: "Authentication", score: 1 },
          { name: "API Docs", type: "document", description: "Documentation", score: 0.5 },
        ]} />
    );
    expect(container.textContent).toContain("Auth Service");
    expect(container.textContent).toContain("Authentication");
    expect(container.textContent).toContain("API Docs");
    expect(container.textContent).toContain("app: 1");
  });
});
