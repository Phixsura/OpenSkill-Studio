import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiHumanEvalPanel } from "@/components/fleet-ai-human-eval-panel";
describe("FleetAiHumanEvalPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiHumanEvalPanel systems={2} active={2} evals={200000} evaluators={200} agreement={90} />);
    expect(container.textContent).toContain("Human Eval");
}); });
