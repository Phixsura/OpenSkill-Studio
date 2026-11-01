import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DepGraphViewer } from "@/components/dep-graph-viewer";

const nodes = [
  { extensionId: "core", version: "1.0", deps: [], status: "resolved" as const },
  { extensionId: "auth", version: "1.0", deps: ["core"], status: "resolved" as const },
  { extensionId: "missing-lib", version: "1.0", deps: [], status: "missing" as const },
];

describe("DepGraphViewer", () => {
  it("renders dependency graph", () => {
    const { container } = render(<DepGraphViewer nodes={nodes} />);
    expect(container.textContent).toContain("core");
    expect(container.textContent).toContain("auth");
    expect(container.textContent).toContain("→ core");
  });
  it("shows empty state", () => {
    const { container } = render(<DepGraphViewer nodes={[]} />);
    expect(container.textContent).toContain("No dependencies");
  });
});
