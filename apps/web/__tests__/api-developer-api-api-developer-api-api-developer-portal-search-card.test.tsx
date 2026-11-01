import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDeveloperApiApiDeveloperPortalSearchCard from "../src/components/api-developer-api-api-developer-api-api-developer-portal-search-card";

const results = [
  { result_id: "r1", title: "GET /api/users", content_preview: "Retrieve all users from the system", result_type: "endpoint", relevance_score: 15 },
];

describe("APIDeveloperAPIApiDeveloperApiApiDeveloperPortalSearchCard", () => {
  it("shows search results", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiDeveloperPortalSearchCard results={results} totalIndexed={500} queryCount={1200} appName="App" />);
    expect(container.textContent).toContain("Portal Search");
    expect(container.textContent).toContain("500 indexed");
    expect(container.textContent).toContain("GET /api/users");
    expect(container.textContent).toContain("endpoint");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiDeveloperPortalSearchCard results={[]} totalIndexed={0} queryCount={0} appName="App" />);
    expect(container.textContent).toContain("No results");
  });
});
