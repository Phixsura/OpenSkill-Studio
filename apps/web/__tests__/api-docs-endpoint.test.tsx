import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ApiDocsEndpoint } from "@/components/api-docs-endpoint";

describe("ApiDocsEndpoint", () => {
  it("shows method and path", () => {
    const { container } = render(<ApiDocsEndpoint method="GET" path="/cohorts" summary="List" scopes={["read:cohorts"]} curlExample="curl ..." />);
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("/cohorts");
  });
  it("shows curl", () => {
    const { container } = render(<ApiDocsEndpoint method="POST" path="/x" summary="Y" scopes={[]} curlExample='curl -X POST "url"' />);
    expect(container.textContent).toContain("curl");
  });
});
