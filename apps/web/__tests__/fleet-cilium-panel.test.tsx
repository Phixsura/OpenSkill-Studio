import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCiliumPanel } from "@/components/fleet-cilium-panel";
describe("FleetCiliumPanel", () => { it("renders", () => {
    const { container } = render(<FleetCiliumPanel agents={10} ready={9} notReady={1} policyEnforced={9} healthy={false} />);
    expect(container.textContent).toContain("Cilium");
    expect(container.textContent).toContain("1 not ready");
}); });
