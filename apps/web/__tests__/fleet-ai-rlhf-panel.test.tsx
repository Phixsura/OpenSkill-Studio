import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiRlhfPanel } from "@/components/fleet-ai-rlhf-panel";
describe("FleetAiRlhfPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiRlhfPanel pipelines={4} active={4} comparisons={5000000} rewardAcc={85} ppoSteps={200000} />);
    expect(container.textContent).toContain("AI RLHF");
}); });
