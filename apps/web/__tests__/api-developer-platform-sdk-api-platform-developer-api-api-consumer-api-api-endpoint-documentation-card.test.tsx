import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-endpoint-documentation-card";

describe("EndpointDocumentationCard", () => {
  it("shows docs", () => {
    const docs = [{ endpoint: "/users", method: "GET", summary: "List all users", tags: ["users"], has_examples: true }];
    const { container } = render(<Card docs={docs} totalDocs={10} undocumentedCount={3} appName="App" />);
    expect(container.textContent).toContain("API Docs");
    expect(container.textContent).toContain("10 documented");
    expect(container.textContent).toContain("3 missing");
    expect(container.textContent).toContain("List all users");
  });
  it("shows empty", () => {
    const { container } = render(<Card docs={[]} totalDocs={0} undocumentedCount={0} appName="App" />);
    expect(container.textContent).toContain("No documentation");
  });
});
