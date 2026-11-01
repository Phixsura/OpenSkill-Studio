import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetGatekeeperPanel } from "@/components/fleet-gatekeeper-panel";
describe("FleetGatekeeperPanel", () => { it("renders", () => {
    const { container } = render(<FleetGatekeeperPanel total={30} enforced={25} auditOnly={5} violations={3} clean={false} />);
    expect(container.textContent).toContain("Gatekeeper");
    expect(container.textContent).toContain("3 violations");
}); });
