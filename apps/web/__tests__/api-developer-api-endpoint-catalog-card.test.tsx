import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIEndpointCatalogCard from "../src/components/api-developer-api-endpoint-catalog-card";

const eps = [{ method: "GET", path: "/api/users", summary: "List", category: "users", deprecated: false }];
const stats = { total: 50, deprecated: 3, categories: 8 };

describe("APIDeveloperAPIEndpointCatalogCard", () => {
  it("shows catalog", () => {
    const { container } = render(<APIDeveloperAPIEndpointCatalogCard endpoints={eps} stats={stats} appName="App" />);
    expect(container.textContent).toContain("Endpoint Catalog");
    expect(container.textContent).toContain("50 endpoints");
    expect(container.textContent).toContain("8 categories");
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("/api/users");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIEndpointCatalogCard endpoints={[]} stats={{ total: 0, deprecated: 0, categories: 0 }} appName="App" />);
    expect(container.textContent).toContain("No endpoints cataloged");
  });
});
