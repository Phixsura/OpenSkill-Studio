import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiModelImpPanel } from "@/components/fleet-ai-model-imp-panel";
describe("FleetAiModelImpPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiModelImpPanel importers={3} active={3} imports={5000} validated={4950} rejected={50} />);
    expect(container.textContent).toContain("Model Import");
}); });
