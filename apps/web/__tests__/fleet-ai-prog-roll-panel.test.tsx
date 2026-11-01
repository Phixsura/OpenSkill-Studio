import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiProgRollPanel } from "@/components/fleet-ai-prog-roll-panel";
describe("FleetAiProgRollPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiProgRollPanel rollouts={5} active={5} currentPct={75} stagesDone={4} totalStages={5} />);
    expect(container.textContent).toContain("Progressive Rollout");
}); });
