import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetVertexAiPanel } from "@/components/fleet-vertex-ai-panel";
describe("FleetVertexAiPanel", () => { it("renders", () => {
    const { container } = render(<FleetVertexAiPanel endpoints={10} deployed={10} models={20} predictions={10000000} />);
    expect(container.textContent).toContain("Vertex AI");
}); });
