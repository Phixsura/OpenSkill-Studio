import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DocsPageViewer } from "@/components/docs-page-viewer";

describe("DocsPageViewer", () => {
  it("renders docs", () => {
    const { container } = render(
      <DocsPageViewer method="GET" path="/api/users" description="List users"
        parameters={[{ name: "page", type: "integer", required: false, description: "Page number" }]}
        responses={{ "200": "Success", "401": "Unauthorized" }} />
    );
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("List users");
    expect(container.textContent).toContain("page");
    expect(container.textContent).toContain("integer");
    expect(container.textContent).toContain("200");
    expect(container.textContent).toContain("Success");
  });
});
