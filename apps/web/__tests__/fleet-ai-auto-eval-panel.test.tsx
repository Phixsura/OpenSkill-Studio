import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiAutoEvalPanel } from "@/components/fleet-ai-auto-eval-panel";
describe("FleetAiAutoEvalPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiAutoEvalPanel evaluators={4} active={4} evals={5000000} correlation={0.95} cost={0.0005} />);
    expect(container.textContent).toContain("Auto Eval");
}); });
