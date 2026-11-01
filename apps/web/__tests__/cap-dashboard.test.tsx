import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CapDashboard } from "@/components/cap-dashboard";

describe("CapDashboard", () => {
  it("renders", () => {
    const { container } = render(
      <CapDashboard overallPct={65} status="critical" criticalCount={1} resourceCount={3}
        critical={[{ name: "memory", type: "compute", pct: 90.6 }]} />
    );
    expect(container.textContent).toContain("Capacity");
    expect(container.textContent).toContain("65%");
    expect(container.textContent).toContain("1 critical");
    expect(container.textContent).toContain("memory");
    expect(container.textContent).toContain("90.6%");
  });
});
