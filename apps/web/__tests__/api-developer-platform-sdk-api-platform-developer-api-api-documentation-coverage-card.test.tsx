import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-documentation-coverage-card";

describe("DocCoverageCard", () => {
  it("shows coverage", () => {
    const docs = [{ endpoint: "/users", method: "GET", coverage_pct: 80, fully_documented: false }];
    const { container } = render(<Card docs={docs} overallCoverage={80} undocumentedCount={1} appName="App" />);
    expect(container.textContent).toContain("Doc Coverage");
    expect(container.textContent).toContain("80%");
    expect(container.textContent).toContain("1 incomplete");
    expect(container.textContent).toContain("/users");
  });
  it("shows 100%", () => {
    const docs = [{ endpoint: "/api", method: "GET", coverage_pct: 100, fully_documented: true }];
    const { container } = render(<Card docs={docs} overallCoverage={100} undocumentedCount={0} appName="App" />);
    expect(container.textContent).toContain("100%");
  });
});
