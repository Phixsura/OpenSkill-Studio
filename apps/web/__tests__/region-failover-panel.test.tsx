import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { RegionFailoverPanel } from "@/components/region-failover-panel";

describe("RegionFailoverPanel", () => {
  it("renders regions", () => {
    const { container } = render(
      <RegionFailoverPanel primary="us-east" failoverNeeded={true} onFailover={vi.fn()}
        regions={[
          { name: "us-east", role: "primary", healthy: false },
          { name: "eu-west", role: "standby", healthy: true },
        ]} />
    );
    expect(container.textContent).toContain("Multi-Region");
    expect(container.textContent).toContain("Failover Needed");
    expect(container.textContent).toContain("us-east");
    expect(container.textContent).toContain("primary");
    expect(container.textContent).toContain("eu-west");
    expect(container.textContent).toContain("Promote");
  });
});
