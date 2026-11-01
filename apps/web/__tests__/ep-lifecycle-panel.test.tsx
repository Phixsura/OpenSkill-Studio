import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { EpLifecyclePanel } from "@/components/ep-lifecycle-panel";
describe("EpLifecyclePanel", () => {
  it("renders", () => {
    const { container } = render(
      <EpLifecyclePanel byState={{ active: 2, deprecated: 1 }}
        endpoints={[
          { path: "/api/v2/users", state: "active", version: "v2", owner: "team-a" },
          { path: "/api/v1/users", state: "deprecated", version: "v1", owner: "team-a" },
        ]} />
    );
    expect(container.textContent).toContain("Endpoint Lifecycle");
    expect(container.textContent).toContain("active: 2");
    expect(container.textContent).toContain("deprecated: 1");
    expect(container.textContent).toContain("/api/v2/users");
    expect(container.textContent).toContain("/api/v1/users");
    expect(container.textContent).toContain("team-a");
  });
});
