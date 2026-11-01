import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetArgoWorkflowV9Panel } from "@/components/fleet-argo-workflow-v9-panel";
describe("FleetArgoWorkflowV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetArgoWorkflowV9Panel workflows={50} running={5} />);
    expect(container.textContent).toContain("Argo Workflow v9");
}); });
