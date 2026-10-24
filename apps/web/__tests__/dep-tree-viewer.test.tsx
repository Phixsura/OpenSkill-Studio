import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DepTreeViewer } from "@/components/dep-tree-viewer";

describe("DepTreeViewer", () => {
  it("renders tree", () => {
    const { container } = render(
      <DepTreeViewer totalNodes={5} maxDepth={2} root="app"
        tree={{
          name: "app", children: [
            { name: "api", children: [{ name: "db", children: [] }] },
            { name: "worker", children: [] },
          ],
        }} />
    );
    expect(container.textContent).toContain("Dependency Tree");
    expect(container.textContent).toContain("5 nodes");
    expect(container.textContent).toContain("depth 2");
    expect(container.textContent).toContain("app");
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("db");
    expect(container.textContent).toContain("worker");
  });
});
