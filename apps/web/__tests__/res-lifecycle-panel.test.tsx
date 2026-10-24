import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ResLifecyclePanel } from "@/components/res-lifecycle-panel";
describe("ResLifecyclePanel", () => {
  it("renders", () => {
    const { container } = render(
      <ResLifecyclePanel total={2} auditEntries={5}
        resources={[
          { id: "vm-1", type: "compute", owner: "alice", version: 3, status: "active" },
          { id: "db-1", type: "database", owner: "bob", version: 1, status: "active" },
        ]} />
    );
    expect(container.textContent).toContain("Resource Lifecycle");
    expect(container.textContent).toContain("2 resources");
    expect(container.textContent).toContain("5 audit entries");
    expect(container.textContent).toContain("vm-1");
    expect(container.textContent).toContain("v3");
    expect(container.textContent).toContain("alice");
  });
});
