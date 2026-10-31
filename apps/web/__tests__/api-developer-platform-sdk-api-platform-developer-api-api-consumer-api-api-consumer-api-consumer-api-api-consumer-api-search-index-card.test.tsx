import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-api-consumer-api-search-index-card";

describe("ConsumerApiSearchIndexCard", () => {
  it("shows results", () => {
    const results = [{ docId: "d1", docType: "endpoint", title: "List Users", snippet: "GET /api/users returns...", score: 2 }];
    const { container } = render(<Card results={results} query="users" totalDocs={50} appName="App" />);
    expect(container.textContent).toContain("Search Index");
    expect(container.textContent).toContain("List Users");
    expect(container.textContent).toContain("endpoint");
    expect(container.textContent).toContain('"users"');
  });
  it("shows no results", () => {
    const { container } = render(<Card results={[]} query="xyz" totalDocs={10} appName="App" />);
    expect(container.textContent).toContain("No results found");
  });
});
