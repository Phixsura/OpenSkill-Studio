import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { OpenApiSpecViewer } from "@/components/openapi-spec-viewer";

describe("OpenApiSpecViewer", () => {
  it("renders spec", () => {
    const { container } = render(
      <OpenApiSpecViewer title="My API" version="1.0.0" endpointCount={10}
        pathCount={6} tags={["users", "system"]} byMethod={{ get: 5, post: 3, delete: 2 }} />
    );
    expect(container.textContent).toContain("My API");
    expect(container.textContent).toContain("v1.0.0");
    expect(container.textContent).toContain("10 endpoints");
    expect(container.textContent).toContain("GET ×5");
    expect(container.textContent).toContain("users");
    expect(container.textContent).toContain("system");
  });
});
