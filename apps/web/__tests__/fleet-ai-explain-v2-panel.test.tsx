import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiExplainV2Panel } from "@/components/fleet-ai-explain-v2-panel";
describe("FleetAiExplainV2Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiExplainV2Panel explainers={4} active={4} explanations={5000000} methods={6} satisfaction={95} />);
    expect(container.textContent).toContain("Explainer v2");
}); });
