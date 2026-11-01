import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ResourceTagMgr } from "@/components/resource-tag-mgr";

describe("ResourceTagMgr", () => {
  it("renders", () => {
    const { container } = render(
      <ResourceTagMgr tagKeys={{ env: 2, team: 1 }}
        resources={[
          { id: "vm-1", tags: { env: "prod", team: "platform" } },
          { id: "vm-2", tags: { env: "staging" } },
        ]} />
    );
    expect(container.textContent).toContain("Resource Tags");
    expect(container.textContent).toContain("2 resources");
    expect(container.textContent).toContain("2 tag keys");
    expect(container.textContent).toContain("vm-1");
    expect(container.textContent).toContain("env=prod");
    expect(container.textContent).toContain("team=platform");
  });
});
