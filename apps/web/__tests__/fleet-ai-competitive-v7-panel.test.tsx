import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiCompetitiveV7Panel } from "@/components/fleet-ai-competitive-v7-panel";
describe("FleetAiCompetitiveV7Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiCompetitiveV7Panel trackers={3} active={3} competitors={50} winRate={80} share={45} ahead={100} />);
    expect(container.textContent).toContain("Competitive v7");
}); });
