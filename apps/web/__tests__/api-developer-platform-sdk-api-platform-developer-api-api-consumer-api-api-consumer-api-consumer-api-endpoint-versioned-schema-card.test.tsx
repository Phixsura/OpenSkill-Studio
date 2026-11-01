import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-endpoint-versioned-schema-card";

describe("EndpointVersionedSchemaCard", () => {
  it("shows versions and compat", () => {
    const versions = [{ version: "v1", fieldCount: 5, deprecatedCount: 1, changelog: "Initial" }];
    const compat = { from: "v1", to: "v2", added: ["email"], removed: [], breaking: false };
    const { container } = render(<Card versions={versions} compat={compat} endpointPath="/api/users" appName="App" />);
    expect(container.textContent).toContain("Versioned Schema");
    expect(container.textContent).toContain("v1");
    expect(container.textContent).toContain("Compatible");
    expect(container.textContent).toContain("+email");
  });
  it("shows empty", () => {
    const { container } = render(<Card versions={[]} compat={null} endpointPath="/api" appName="App" />);
    expect(container.textContent).toContain("No schema versions");
  });
});
