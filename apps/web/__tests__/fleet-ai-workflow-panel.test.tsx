import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiWorkflowPanel } from "@/components/fleet-ai-workflow-panel";
describe("FleetAiWorkflowPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiWorkflowPanel workflows={20} active={20} executions={500000} steps={1000} />);
    expect(container.textContent).toContain("AI Workflow");
}); });
