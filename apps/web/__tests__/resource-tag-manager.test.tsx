import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ResourceTagManager } from "@/components/resource-tag-manager";

describe("ResourceTagManager", () => {
  it("renders tags", () => {
    const { container } = render(
      <ResourceTagManager onTag={vi.fn()} tagKeys={["env", "team"]} resources={[
        { id: "i-001", tags: { env: "prod", team: "platform" } },
        { id: "i-002", tags: { env: "staging" } },
      ]} />
    );
    expect(container.textContent).toContain("Resource Tags");
    expect(container.textContent).toContain("2 resources");
    expect(container.textContent).toContain("i-001");
    expect(container.textContent).toContain("prod");
    expect(container.textContent).toContain("platform");
  });
});
