import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiRelScorePanel } from "@/components/fleet-ai-rel-score-panel";
describe("FleetAiRelScorePanel", () => { it("renders", () => {
    const { container } = render(<FleetAiRelScorePanel scorers={3} active={3} score={99} availability={99.999} durability={99.9999} />);
    expect(container.textContent).toContain("Reliability Score");
}); });
