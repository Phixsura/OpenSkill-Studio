import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiModelObsV2Panel } from "@/components/fleet-ai-model-obs-v2-panel";
describe("FleetAiModelObsV2Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiModelObsV2Panel systems={4} active={4} models={1000} metrics={500000000} traces={200000000} logs={2000000000} />);
    expect(container.textContent).toContain("Model Observability v2");
}); });
