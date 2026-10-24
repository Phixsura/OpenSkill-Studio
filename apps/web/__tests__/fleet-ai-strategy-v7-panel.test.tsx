import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiStrategyV7Panel } from "@/components/fleet-ai-strategy-v7-panel";
describe("FleetAiStrategyV7Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiStrategyV7Panel planners={3} active={3} initiatives={100} completed={80} okrs={30} onTrack={95} />);
    expect(container.textContent).toContain("Strategy v7");
}); });
