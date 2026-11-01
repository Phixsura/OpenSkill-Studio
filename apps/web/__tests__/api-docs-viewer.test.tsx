import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ApiDocsViewer } from "@/components/api-docs-viewer";

describe("ApiDocsViewer", () => {
  it("renders docs", () => {
    const { container } = render(
      <ApiDocsViewer title="OpenSkill API" version="3.0.0" operationCount={2} tags={["Users"]}
        paths={{
          "/api/v1/users": {
            get: { summary: "List users", description: "", tag: "Users", authRequired: true },
            post: { summary: "Create user", description: "", tag: "Users", authRequired: true },
          }
        }} />
    );
    expect(container.textContent).toContain("OpenSkill API");
    expect(container.textContent).toContain("v3.0.0");
    expect(container.textContent).toContain("2 operations");
    expect(container.textContent).toContain("get");
    expect(container.textContent).toContain("/api/v1/users");
    expect(container.textContent).toContain("List users");
  });
});
