import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiModelCascPanel } from "@/components/fleet-ai-model-casc-panel";
describe("FleetAiModelCascPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiModelCascPanel cascades={3} active={3} requests={50000000} avgDepth={3} saved={50} />);
    expect(container.textContent).toContain("Model Cascade");
}); });
