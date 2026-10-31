import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDeveloperApiApiApiDocumentationGeneratorCard from "../src/components/api-developer-api-api-developer-api-api-api-documentation-generator-card";

const endpoints = [
  { method: "GET", path: "/api/users", summary: "List users", tags: ["users"], has_examples: true },
  { method: "POST", path: "/api/users", summary: "Create user", tags: ["users"], has_examples: false },
];

describe("Card", () => {
  it("shows docs", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiApiDocumentationGeneratorCard title="My API" version="2.0" endpoints={endpoints} documentedPct={50} appName="App" />);
    expect(container.textContent).toContain("API Docs Generator");
    expect(container.textContent).toContain("My API v2.0");
    expect(container.textContent).toContain("50% with examples");
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("/api/users");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiApiDocumentationGeneratorCard title="API" version="1.0" endpoints={[]} documentedPct={0} appName="App" />);
    expect(container.textContent).toContain("No endpoints documented");
  });
});
