import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ResLifecyclePanel } from "@/components/res-lifecycle-panel";

describe("ResLifecyclePanel", () => {
  it("renders", () => {
    const { container } = render(
      <ResLifecyclePanel total={50} active={45} expired={3} orphaned={2}
        needsCleanup={5} byType={{ compute: 30, storage: 15, network: 5 }} />
    );
    expect(container.textContent).toContain("Resource Lifecycle");
    expect(container.textContent).toContain("50 resources");
    expect(container.textContent).toContain("5 cleanup");
    expect(container.textContent).toContain("45");
    expect(container.textContent).toContain("3");
  });
});
