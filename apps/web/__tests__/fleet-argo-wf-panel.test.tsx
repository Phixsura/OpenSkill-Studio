import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetArgoWfPanel } from "@/components/fleet-argo-wf-panel";
describe("FleetArgoWfPanel", () => { it("renders", () => {
    const { container } = render(<FleetArgoWfPanel total={50} succeeded={45} failed={3} running={2} avgDuration={12} />);
    expect(container.textContent).toContain("Argo Workflows");
    expect(container.textContent).toContain("avg 12min");
}); });
