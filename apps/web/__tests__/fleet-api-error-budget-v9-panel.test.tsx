import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiErrorBudgetV9Panel } from "@/components/fleet-api-error-budget-v9-panel";
describe("FleetApiErrorBudgetV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiErrorBudgetV9Panel apis={50} remaining={90} />);
    expect(container.textContent).toContain("API Error Budget v9");
}); });
