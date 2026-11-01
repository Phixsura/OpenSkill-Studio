import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiTokenBudgPanel } from "@/components/fleet-ai-token-budg-panel";
describe("FleetAiTokenBudgPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiTokenBudgPanel budgets={5} active={5} allocated={500000000} used={350000000} utilization={70} cost={7500} />);
    expect(container.textContent).toContain("Token Budget");
}); });
