import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { GraphqlSchemaExplorer } from "@/components/graphql-schema-explorer";

describe("GraphqlSchemaExplorer", () => {
  it("renders schema", () => {
    const { container } = render(
      <GraphqlSchemaExplorer analysis={{
        totalTypes: 5, byKind: { OBJECT: 4, ENUM: 1 }, totalFields: 8,
        queries: ["users", "apps"], mutations: ["createApp"], complexity: "low",
      }} />
    );
    expect(container.textContent).toContain("GraphQL Schema");
    expect(container.textContent).toContain("low complexity");
    expect(container.textContent).toContain("5");
    expect(container.textContent).toContain("users");
    expect(container.textContent).toContain("createApp");
    expect(container.textContent).toContain("Queries (2)");
    expect(container.textContent).toContain("Mutations (1)");
  });
});
