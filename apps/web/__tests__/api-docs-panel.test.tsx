import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ApiDocsPanel } from "@/components/api-docs-panel";

describe("ApiDocsPanel", () => {
  it("renders", () => {
    const { container } = render(
      <ApiDocsPanel title="MyAPI" version="2.0" docCoverage={66.7} tags={["users", "orders"]}
        endpoints={[
          { path: "/users", method: "GET", summary: "List users", tag: "users" },
          { path: "/users", method: "POST", summary: "Create user", tag: "users" },
        ]} />
    );
    expect(container.textContent).toContain("MyAPI v2.0");
    expect(container.textContent).toContain("2 endpoints");
    expect(container.textContent).toContain("66.7% documented");
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("/users");
    expect(container.textContent).toContain("List users");
  });
});
