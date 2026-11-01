import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { EpCatalogBrowser } from "@/components/ep-catalog-browser";

describe("EpCatalogBrowser", () => {
  it("renders", () => {
    const { container } = render(
      <EpCatalogBrowser total={10} tags={["users", "system"]}
        byMethod={{ GET: 6, POST: 4 }} onSearch={vi.fn()}
        endpoints={[
          { path: "/api/users", method: "GET", tag: "users", description: "List users" },
          { path: "/api/health", method: "GET", tag: "system", description: "Health" },
        ]} />
    );
    expect(container.textContent).toContain("API Catalog");
    expect(container.textContent).toContain("10 endpoints");
    expect(container.textContent).toContain("2 tags");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("List users");
  });
});
