import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIOpenAPIDiffCheckerCard from "../src/components/api-developer-api-openapi-diff-checker-card";

const diffs = [
  { diff_id: "d1", change_type: "breaking", category: "endpoint_removed", path: "/api/old", description: "Removed" },
  { diff_id: "d2", change_type: "non_breaking", category: "endpoint_added", path: "/api/new", description: "Added" },
];

describe("APIDeveloperAPIOpenAPIDiffCheckerCard", () => {
  it("shows diff report", () => {
    const { container } = render(<APIDeveloperAPIOpenAPIDiffCheckerCard fromVersion="v1" toVersion="v2" diffs={diffs} breakingCount={1} appName="App" />);
    expect(container.textContent).toContain("API Diff Checker");
    expect(container.textContent).toContain("v1 → v2");
    expect(container.textContent).toContain("1 breaking");
    expect(container.textContent).toContain("/api/old");
    expect(container.textContent).toContain("endpoint_removed");
  });
  it("shows compatible", () => {
    const { container } = render(<APIDeveloperAPIOpenAPIDiffCheckerCard fromVersion="v1" toVersion="v2" diffs={[]} breakingCount={0} appName="App" />);
    expect(container.textContent).toContain("compatible");
  });
});
