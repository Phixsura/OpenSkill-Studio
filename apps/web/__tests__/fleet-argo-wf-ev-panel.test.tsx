import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetArgoWfEvPanel } from "@/components/fleet-argo-wf-ev-panel";
describe("FleetArgoWfEvPanel", () => { it("renders", () => {
    const { container } = render(<FleetArgoWfEvPanel totalEvents={100} triggeredWorkflows={30} triggerRate={30} />);
    expect(container.textContent).toContain("Argo WF Events");
}); });
