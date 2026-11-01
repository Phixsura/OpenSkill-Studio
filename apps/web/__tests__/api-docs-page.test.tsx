import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ApiDocsPage } from "@/components/api-docs-page";

describe("ApiDocsPage", () => {
  const sections = [{
    id: "apps", title: "Apps", icon: "📦", endpointCount: 2,
    endpoints: [
      { method: "GET", path: "/api/v1/apps", fullUrl: "https://api.x.dev/api/v1/apps", summary: "List apps" },
      { method: "POST", path: "/api/v1/apps", fullUrl: "https://api.x.dev/api/v1/apps", summary: "Create app" },
    ],
  }];
  it("renders docs", () => {
    const { container } = render(
      <ApiDocsPage sections={sections} totalEndpoints={2} baseUrl="https://api.x.dev" />
    );
    expect(container.textContent).toContain("Apps");
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("/api/v1/apps");
    expect(container.textContent).toContain("List apps");
  });
});
