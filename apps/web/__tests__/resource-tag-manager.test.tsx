import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ResourceTagManager } from "@/components/resource-tag-manager";

describe("ResourceTagManager", () => {
  it("renders tags", () => {
    const { container } = render(
      <ResourceTagManager onTag={vi.fn()} tagDistribution={{ env: 2, team: 2 }}
        resources={[
          { id: "app-1", tags: { env: "prod", team: "platform" } },
          { id: "db-1", tags: { env: "prod", team: "data" } },
        ]} />
    );
    expect(container.textContent).toContain("Resource Tags");
    expect(container.textContent).toContain("2 resources");
    expect(container.textContent).toContain("env: 2");
    expect(container.textContent).toContain("app-1");
    expect(container.textContent).toContain("env=prod");
    expect(container.textContent).toContain("Edit Tags");
  });
});
