import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { GraphqlExplorer } from "@/components/graphql-explorer";

describe("GraphqlExplorer", () => {
  const types = [
    { name: "Query", kind: "OBJECT", fieldCount: 2, description: "", fields: [
      { name: "app", type: "App", description: "Get app", deprecated: false },
    ]},
    { name: "App", kind: "OBJECT", fieldCount: 2, description: "An application", fields: [] },
  ];
  it("renders types", () => {
    const { container } = render(<GraphqlExplorer types={types} queryCount={2} mutationCount={0} />);
    expect(container.textContent).toContain("Query");
    expect(container.textContent).toContain("App");
    expect(container.textContent).toContain("2 types");
    expect(container.textContent).toContain("2 queries");
  });
});
