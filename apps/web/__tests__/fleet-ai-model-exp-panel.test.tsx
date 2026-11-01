import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiModelExpPanel } from "@/components/fleet-ai-model-exp-panel";
describe("FleetAiModelExpPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiModelExpPanel exporters={3} active={3} exports={20000} formats={8} sizeGb={5000} />);
    expect(container.textContent).toContain("Model Export");
}); });
