import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiModelCapPanel } from "@/components/fleet-ai-model-cap-panel";
describe("FleetAiModelCapPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiModelCapPanel planners={3} active={3} models={200} maxRps={2000000} utilization={60} />);
    expect(container.textContent).toContain("Model Capacity");
}); });
