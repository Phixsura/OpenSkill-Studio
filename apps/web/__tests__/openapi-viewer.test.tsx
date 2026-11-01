import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { OpenApiViewer } from "@/components/openapi-viewer";

describe("OpenApiViewer", () => {
  const endpoints = [
    { method: "GET", path: "/apps", operationId: "listApps", hasSummary: true, tags: ["apps"] },
    { method: "POST", path: "/apps", operationId: "createApp", hasSummary: true, tags: ["apps"] },
  ];
  it("renders spec", () => {
    const { container } = render(
      <OpenApiViewer title="My API" version="3.0.0" valid={true} endpoints={endpoints} errors={[]} warnings={[]} />
    );
    expect(container.textContent).toContain("My API");
    expect(container.textContent).toContain("3.0.0");
    expect(container.textContent).toContain("Valid");
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("/apps");
  });
});
