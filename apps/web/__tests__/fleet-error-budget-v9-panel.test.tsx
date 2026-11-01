import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetErrorBudgetV9Panel } from "@/components/fleet-error-budget-v9-panel";
describe("FleetErrorBudgetV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetErrorBudgetV9Panel slos={20} remaining={90} />);
    expect(container.textContent).toContain("Error Budget v9");
}); });
