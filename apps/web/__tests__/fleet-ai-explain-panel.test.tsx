import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiExplainPanel } from "@/components/fleet-ai-explain-panel";
describe("FleetAiExplainPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiExplainPanel services={5} active={5} explanations={2000000} models={50} />);
    expect(container.textContent).toContain("Explainability");
}); });
