import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ResourceLimitCard } from "@/components/resource-limit-card";

describe("ResourceLimitCard", () => {
  const resources = [
    { resource: "cpu_cores", limit: 2, current: 1.5, unlimited: false },
    { resource: "bandwidth_gb", limit: -1, current: 50, unlimited: true },
  ];
  it("renders", () => {
    const { container } = render(
      <ResourceLimitCard plan="pro" resources={resources} onUpgrade={vi.fn()} />
    );
    expect(container.textContent).toContain("Resource Limits");
    expect(container.textContent).toContain("pro");
    expect(container.textContent).toContain("CPU Cores");
    expect(container.textContent).toContain("1.5 / 2");
    expect(container.textContent).toContain("50 / ∞");
  });
});
