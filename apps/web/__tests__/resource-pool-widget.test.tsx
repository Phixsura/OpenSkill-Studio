import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ResourcePoolWidget } from "@/components/resource-pool-widget";

describe("ResourcePoolWidget", () => {
  it("renders", () => {
    const { container } = render(
      <ResourcePoolWidget pools={[
        { pool: "gpu", capacity: 10, used: 4, available: 6, utilizationPct: 40, owners: 2 },
        { pool: "cpu", capacity: 100, used: 95, available: 5, utilizationPct: 95, owners: 5 },
      ]} />
    );
    expect(container.textContent).toContain("Resource Pools");
    expect(container.textContent).toContain("2 pools");
    expect(container.textContent).toContain("gpu");
    expect(container.textContent).toContain("4/10");
    expect(container.textContent).toContain("cpu");
    expect(container.textContent).toContain("95/100");
  });
});
