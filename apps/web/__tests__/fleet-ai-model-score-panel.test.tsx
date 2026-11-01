import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiModelScorePanel } from "@/components/fleet-ai-model-score-panel";
describe("FleetAiModelScorePanel", () => { it("renders", () => {
    const { container } = render(<FleetAiModelScorePanel scorers={3} active={3} models={500} avgScore={95} dimensions={15} />);
    expect(container.textContent).toContain("Model Scoring");
}); });
