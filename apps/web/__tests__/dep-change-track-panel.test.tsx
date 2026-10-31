import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DepChangeTrackPanel } from "@/components/dep-change-track-panel";
describe("DepChangeTrackPanel", () => {
  it("renders", () => {
    const { container } = render(
      <DepChangeTrackPanel totalAdded={2} totalRemoved={1} hasRemovals={true}
        changes={[
          { service: "api", added: ["new-svc"], removed: ["old-svc"], risk: "high" },
          { service: "worker", added: ["s3"], removed: [], risk: "low" },
        ]} />
    );
    expect(container.textContent).toContain("Dependency Changes");
    expect(container.textContent).toContain("+2 added");
    expect(container.textContent).toContain("-1 removed");
    expect(container.textContent).toContain("api:");
    expect(container.textContent).toContain("+new-svc");
    expect(container.textContent).toContain("-old-svc");
  });
});
