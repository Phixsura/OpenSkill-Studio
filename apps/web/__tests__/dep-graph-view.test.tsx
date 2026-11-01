import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DepGraphView } from "@/components/dep-graph-view";

describe("DepGraphView", () => {
  it("renders graph", () => {
    const { container } = render(
      <DepGraphView roots={["app"]} leaves={["db"]}
        nodes={[{ id: "app", in: 0, out: 2 }, { id: "db", in: 2, out: 0 }]}
        edges={[{ source: "app", target: "db", type: "runtime" }]} />
    );
    expect(container.textContent).toContain("Dependency Graph");
    expect(container.textContent).toContain("2 nodes");
    expect(container.textContent).toContain("1 edges");
    expect(container.textContent).toContain("app");
    expect(container.textContent).toContain("db");
  });
});
