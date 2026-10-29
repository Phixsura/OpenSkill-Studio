import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIEndpointDocumentationCard from "../src/components/api-endpoint-documentation-card";

const docs = [{ method: "GET", path: "/api/users", summary: "List users", param_count: 2 }];

describe("APIEndpointDocumentationCard", () => {
  it("shows docs", () => {
    const { container } = render(<APIEndpointDocumentationCard docs={docs} undocumentedCount={3} appName="App" />);
    expect(container.textContent).toContain("Endpoint Docs");
    expect(container.textContent).toContain("3 missing");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("2 params");
  });
  it("shows empty", () => {
    const { container } = render(<APIEndpointDocumentationCard docs={[]} undocumentedCount={0} appName="App" />);
    expect(container.textContent).toContain("No endpoint documentation");
  });
});
