import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-openapi-diff-card";

describe("OpenapiDiffCard", () => {
  it("shows diff", () => {
    const changes = [{ change_type: "endpoint_added", path: "/orders", detail: "New endpoint: /orders", breaking: false }, { change_type: "endpoint_removed", path: "/legacy", detail: "Removed: /legacy", breaking: true }];
    const { container } = render(<Card versionFrom="v1" versionTo="v2" changes={changes} breakingCount={1} nonBreakingCount={1} appName="App" />);
    expect(container.textContent).toContain("API Diff");
    expect(container.textContent).toContain("v1 → v2");
    expect(container.textContent).toContain("1 breaking");
    expect(container.textContent).toContain("New endpoint");
  });
  it("shows no changes", () => {
    const { container } = render(<Card versionFrom="v1" versionTo="v2" changes={[]} breakingCount={0} nonBreakingCount={0} appName="App" />);
    expect(container.textContent).toContain("No changes detected");
  });
});
