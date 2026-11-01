import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSlBudgetPanel } from "@/components/fleet-sl-budget-panel";
describe("FleetSlBudgetPanel", () => { it("renders", () => {
    const { container } = render(<FleetSlBudgetPanel total={5} exhausted={1} low={1} healthy={3} alert={true} />);
    expect(container.textContent).toContain("SL Budget");
    expect(container.textContent).toContain("Budget exhausted");
}); });
