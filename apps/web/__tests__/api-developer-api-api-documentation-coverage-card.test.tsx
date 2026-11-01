import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDocumentationCoverageCard from "../src/components/api-developer-api-api-documentation-coverage-card";

const endpoints = [
  { endpoint: "/api/users", method: "GET", coverage_score: 4, fully_documented: true },
  { endpoint: "/api/orders", method: "POST", coverage_score: 1, fully_documented: false },
];

describe("APIDeveloperAPIApiDocumentationCoverageCard", () => {
  it("shows doc coverage", () => {
    const { container } = render(<APIDeveloperAPIApiDocumentationCoverageCard endpoints={endpoints} coveragePct={62.5} fullyDocumentedCount={1} appName="App" />);
    expect(container.textContent).toContain("Doc Coverage");
    expect(container.textContent).toContain("62.5%");
    expect(container.textContent).toContain("1/2 complete");
    expect(container.textContent).toContain("/api/orders");
    expect(container.textContent).toContain("1/4");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiDocumentationCoverageCard endpoints={[]} coveragePct={0} fullyDocumentedCount={0} appName="App" />);
    expect(container.textContent).toContain("No endpoints registered");
  });
});
