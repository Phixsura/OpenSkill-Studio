import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { GraphqlSchemaExplorer } from "@/components/graphql-schema-explorer";

describe("GraphqlSchemaExplorer", () => {
  const types = [{ name: "App", fields: [
    { name: "id", type: "ID", required: true },
    { name: "name", type: "String" },
  ]}];
  it("renders", () => {
    const { container } = render(
      <GraphqlSchemaExplorer types={types} queryCount={3} mutationCount={2} schema="type App { id: ID! }" />
    );
    expect(container.textContent).toContain("GraphQL Schema");
    expect(container.textContent).toContain("App");
    expect(container.textContent).toContain("1 types");
    expect(container.textContent).toContain("3 queries");
    expect(container.textContent).toContain("ID");
  });
});
