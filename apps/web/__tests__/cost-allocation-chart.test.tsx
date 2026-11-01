import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CostAllocationChart } from "@/components/cost-allocation-chart";

describe("CostAllocationChart", () => {
  it("renders allocations", () => {
    const allocs = [{ app_id: "app-1", cost_cents: 7000, pct: 70 }, { app_id: "app-2", cost_cents: 3000, pct: 30 }];
    const { container } = render(<CostAllocationChart allocations={allocs} totalCents={10000} period="Oct 2026" />);
    expect(container.textContent).toContain("$100.00");
    expect(container.textContent).toContain("app-1");
    expect(container.textContent).toContain("70%");
    expect(container.textContent).toContain("Oct 2026");
  });
});
