import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIGraphQLQueryAnalyzerCard from "../src/components/api-developer-api-graphql-query-analyzer-card";

const analyses = [
  { query_id: "q1", depth: 3, field_count: 8, estimated_cost: 24, has_introspection: false, warnings: [] },
  { query_id: "q2", depth: 6, field_count: 15, estimated_cost: 90, has_introspection: true, warnings: ["Too deep"] },
];

describe("APIDeveloperAPIGraphQLQueryAnalyzerCard", () => {
  it("shows analyses", () => {
    const { container } = render(<APIDeveloperAPIGraphQLQueryAnalyzerCard analyses={analyses} expensiveCount={1} appName="App" />);
    expect(container.textContent).toContain("GraphQL Analyzer");
    expect(container.textContent).toContain("1 expensive");
    expect(container.textContent).toContain("depth:3");
    expect(container.textContent).toContain("cost:24");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIGraphQLQueryAnalyzerCard analyses={[]} expensiveCount={0} appName="App" />);
    expect(container.textContent).toContain("No queries analyzed");
  });
});
