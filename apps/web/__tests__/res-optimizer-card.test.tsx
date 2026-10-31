import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ResOptimizerCard } from "@/components/res-optimizer-card";

describe("ResOptimizerCard", () => {
  it("renders optimizer", () => {
    const { container } = render(
      <ResOptimizerCard totalWasteCost="$230/mo" wasteCount={2} onOptimize={vi.fn()}
        wastedResources={[
          { name: "idle-vm", usagePct: 2, cost: 200, wastedCost: 180, action: "terminate_or_downsize" },
          { name: "dev-db", usagePct: 25, cost: 100, wastedCost: 50, action: "rightsize" },
        ]} />
    );
    expect(container.textContent).toContain("Resource Optimizer");
    expect(container.textContent).toContain("Save $230/mo");
    expect(container.textContent).toContain("idle-vm");
    expect(container.textContent).toContain("2% used");
    expect(container.textContent).toContain("Remove");
    expect(container.textContent).toContain("Resize");
  });
});
