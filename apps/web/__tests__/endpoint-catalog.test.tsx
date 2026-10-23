import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { EndpointCatalog } from "@/components/endpoint-catalog";

describe("EndpointCatalog", () => {
  it("renders endpoints", () => {
    const { container } = render(
      <EndpointCatalog categories={[{ category: "apps", count: 2 }]}
        endpoints={[
          { method: "GET", path: "/api/v1/apps", description: "List apps", auth: true, category: "apps" },
          { method: "POST", path: "/api/v1/apps", description: "Create app", auth: true, category: "apps" },
        ]} />
    );
    expect(container.textContent).toContain("API Endpoints");
    expect(container.textContent).toContain("apps (2)");
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("/api/v1/apps");
    expect(container.textContent).toContain("List apps");
  });
});
