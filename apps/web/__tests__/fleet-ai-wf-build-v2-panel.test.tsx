import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiWfBuildV2Panel } from "@/components/fleet-ai-wf-build-v2-panel";
describe("FleetAiWfBuildV2Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiWfBuildV2Panel builders={3} active={3} workflows={1000} nodes={10000} executions={200000} />);
    expect(container.textContent).toContain("Workflow Builder v2");
}); });
