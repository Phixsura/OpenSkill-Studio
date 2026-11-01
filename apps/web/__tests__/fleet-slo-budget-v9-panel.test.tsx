import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSloBudgetV9Panel } from "@/components/fleet-slo-budget-v9-panel";
describe("FleetSloBudgetV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetSloBudgetV9Panel slos={20} avgBudget={88} />);
    expect(container.textContent).toContain("SLO Budget v9");
}); });
