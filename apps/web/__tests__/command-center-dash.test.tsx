import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CommandCenterDash } from "@/components/command-center-dash";

describe("CommandCenterDash", () => {
  it("renders center", () => {
    const { container } = render(
      <CommandCenterDash score={95} status="green"
        services={{ total: 10, healthyPct: 100, unhealthy: 0 }}
        deployments={{ successRate: 98, failed: 0 }}
        alerts={{ total: 5, critical: 0 }} actionItems={[]} />
    );
    expect(container.textContent).toContain("95");
    expect(container.textContent).toContain("All Systems Go");
    expect(container.textContent).toContain("100%");
    expect(container.textContent).toContain("98%");
  });
});
