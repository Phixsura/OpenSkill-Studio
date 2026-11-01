import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIGraphQLSchemaCard from "../src/components/api-graphql-schema-card";

const stats = { types: 5, fields: 20, queries: 3, mutations: 2 };
const types = [
  { type_name: "User", kind: "type", field_count: 5 },
  { type_name: "CreateUserInput", kind: "input", field_count: 3 },
];

describe("APIGraphQLSchemaCard", () => {
  it("renders header and stats", () => {
    const { container } = render(<APIGraphQLSchemaCard stats={stats} types={types} appName="App" />);
    expect(container.textContent).toContain("GraphQL Schema");
    expect(container.textContent).toContain("5 types");
    expect(container.textContent).toContain("3");
    expect(container.textContent).toContain("queries");
  });

  it("shows type list", () => {
    const { container } = render(<APIGraphQLSchemaCard stats={stats} types={types} appName="App" />);
    expect(container.textContent).toContain("User");
    expect(container.textContent).toContain("input");
    expect(container.textContent).toContain("5 fields");
  });
});
