import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetServiceBudgetV9Panel } from "@/components/fleet-service-budget-v9-panel";
describe("FleetServiceBudgetV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetServiceBudgetV9Panel services={100} overBudget={0} />);
    expect(container.textContent).toContain("Service Budget v9");
}); });
