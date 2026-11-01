import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetWorkflowEngineV9Panel } from "@/components/fleet-workflow-engine-v9-panel";
describe("FleetWorkflowEngineV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetWorkflowEngineV9Panel total={50} running={10} />);
    expect(container.textContent).toContain("Workflow Engine v9");
}); });
