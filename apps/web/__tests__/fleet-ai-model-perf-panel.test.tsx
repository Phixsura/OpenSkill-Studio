import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiModelPerfPanel } from "@/components/fleet-ai-model-perf-panel";
describe("FleetAiModelPerfPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiModelPerfPanel trackers={5} active={5} models={500} metrics={5000} alerts={10} />);
    expect(container.textContent).toContain("Model Performance");
}); });
