import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiEvalPanel } from "@/components/fleet-ai-eval-panel";
describe("FleetAiEvalPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiEvalPanel pipelines={10} active={10} evaluations={50000} metrics={100} />);
    expect(container.textContent).toContain("AI Evaluation");
}); });
