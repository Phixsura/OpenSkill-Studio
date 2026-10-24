import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiErrBudgetPanel } from "@/components/fleet-ai-err-budget-panel";
describe("FleetAiErrBudgetPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiErrBudgetPanel budgets={5} active={5} remaining={80} burnRate={0.3} slos={30} />);
    expect(container.textContent).toContain("Error Budget");
}); });
