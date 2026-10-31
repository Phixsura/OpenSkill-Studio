import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiWfEnginePanel } from "@/components/fleet-ai-wf-engine-panel";
describe("FleetAiWfEnginePanel", () => { it("renders", () => {
    const { container } = render(<FleetAiWfEnginePanel engines={4} active={4} workflows={100000} steps={1000000} duration={20} />);
    expect(container.textContent).toContain("Workflow Engine");
}); });
