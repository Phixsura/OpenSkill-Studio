import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-graphql-schema-registry-card";

describe("GraphqlSchemaRegistryCard", () => {
  it("shows registries", () => {
    const registries = [{ registry_id: "r1", service_name: "users-api", current_version: "v2", version_count: 2, latest: { version: "v2", type_count: 7, query_count: 4, mutation_count: 3 } }];
    const { container } = render(<Card registries={registries} appName="App" />);
    expect(container.textContent).toContain("GraphQL Schemas");
    expect(container.textContent).toContain("users-api");
    expect(container.textContent).toContain("v2");
    expect(container.textContent).toContain("7 types");
  });
  it("shows empty", () => {
    const { container } = render(<Card registries={[]} appName="App" />);
    expect(container.textContent).toContain("No schemas registered");
  });
});
