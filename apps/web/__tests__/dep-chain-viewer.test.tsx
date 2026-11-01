import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DepChainViewer } from "@/components/dep-chain-viewer";

describe("DepChainViewer", () => {
  it("renders", () => {
    const { container } = render(
      <DepChainViewer serviceCount={4} maxDepth={3} criticalPaths={["web"]}
        chains={{
          web: { chain: ["web", "api", "auth", "db"], depth: 3 },
          api: { chain: ["api", "auth", "db"], depth: 2 },
          db: { chain: ["db"], depth: 0 },
        }} />
    );
    expect(container.textContent).toContain("Dependency Chains");
    expect(container.textContent).toContain("4 services");
    expect(container.textContent).toContain("max depth 3");
    expect(container.textContent).toContain("1 critical");
    expect(container.textContent).toContain("web → api → auth → db");
  });
});
