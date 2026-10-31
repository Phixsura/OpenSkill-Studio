import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ApiDepGraph } from "@/components/api-dep-graph";

describe("ApiDepGraph", () => {
  it("renders", () => {
    const { container } = render(
      <ApiDepGraph nodeCount={4} totalCalls={9000} nodes={["web", "api", "db", "cache"]}
        edges={[
          { source: "api", target: "db", calls: 5000, avgMs: 5 },
          { source: "api", target: "cache", calls: 3000, avgMs: 1 },
        ]} />
    );
    expect(container.textContent).toContain("API Dependency Graph");
    expect(container.textContent).toContain("4 services");
    expect(container.textContent).toContain("9,000 calls");
    expect(container.textContent).toContain("api → db");
    expect(container.textContent).toContain("5,000 calls");
  });
});
