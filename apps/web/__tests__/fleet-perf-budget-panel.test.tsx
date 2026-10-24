import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetPerfBudgetPanel } from "@/components/fleet-perf-budget-panel";
describe("FleetPerfBudgetPanel", () => { it("renders", () => {
    const { container } = render(<FleetPerfBudgetPanel total={20} withinBudget={18} overBudget={2} compliant={false} />);
    expect(container.textContent).toContain("Perf Budget");
    expect(container.textContent).toContain("2/20 over");
}); });
