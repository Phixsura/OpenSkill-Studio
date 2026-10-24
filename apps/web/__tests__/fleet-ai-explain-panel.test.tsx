import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiExplainPanel } from "@/components/fleet-ai-explain-panel";
describe("FleetAiExplainPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiExplainPanel engines={3} active={3} explanations={500000} methods={["SHAP", "LIME"]} coverage={95} />);
    expect(container.textContent).toContain("Explainability");
}); });
