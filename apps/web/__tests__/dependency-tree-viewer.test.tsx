import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DependencyTreeViewer } from "@/components/dependency-tree-viewer";

describe("DependencyTreeViewer", () => {
  it("shows resolved", () => {
    const { container } = render(
      <DependencyTreeViewer installOrder={["auth", "db"]} unresolved={[]} canInstall={true} />
    );
    expect(container.textContent).toContain("All resolved");
    expect(container.textContent).toContain("auth");
  });
  it("shows missing", () => {
    const { container } = render(
      <DependencyTreeViewer installOrder={[]} unresolved={["redis-lib"]} canInstall={false} />
    );
    expect(container.textContent).toContain("Missing dependencies");
    expect(container.textContent).toContain("redis-lib");
  });
});
