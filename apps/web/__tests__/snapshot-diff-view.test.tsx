import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SnapshotDiffView } from "@/components/snapshot-diff-view";

describe("SnapshotDiffView", () => {
  it("shows drift", () => {
    const { container } = render(
      <SnapshotDiffView added={{ region: "us-east" }} removed={{ name: "App" }}
        changed={{ port: { before: 3000, after: 8080 } }} totalChanges={3} hasDrift={true} />
    );
    expect(container.textContent).toContain("3 changes");
    expect(container.textContent).toContain("port");
    expect(container.textContent).toContain("3000");
    expect(container.textContent).toContain("8080");
    expect(container.textContent).toContain("region");
  });
  it("no drift", () => {
    const { container } = render(
      <SnapshotDiffView added={{}} removed={{}} changed={{}} totalChanges={0} hasDrift={false} />
    );
    expect(container.textContent).toContain("No drift");
  });
});
