import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetWorkersAiPanel } from "@/components/fleet-workers-ai-panel";
describe("FleetWorkersAiPanel", () => { it("renders", () => {
    const { container } = render(<FleetWorkersAiPanel models={10} active={10} inferences={2000000} avgLatency={80} />);
    expect(container.textContent).toContain("Workers AI");
}); });
