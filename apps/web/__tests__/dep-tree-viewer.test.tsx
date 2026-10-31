import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DepTreeViewer } from "@/components/dep-tree-viewer";

describe("DepTreeViewer", () => {
  it("renders", () => {
    const { container } = render(
      <DepTreeViewer roots={["api"]} maxDepth={3} edges={3} hasCycles={false}
        tree={{ api: ["auth", "db"], auth: ["db"] }} />
    );
    expect(container.textContent).toContain("Dependency Tree");
    expect(container.textContent).toContain("1 roots");
    expect(container.textContent).toContain("depth 3");
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("auth");
    expect(container.textContent).toContain("db");
  });
});
