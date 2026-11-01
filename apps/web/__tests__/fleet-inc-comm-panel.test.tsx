import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetIncCommPanel } from "@/components/fleet-inc-comm-panel";
describe("FleetIncCommPanel", () => { it("renders", () => {
    const { container } = render(<FleetIncCommPanel total={10} notified={8} notNotified={2} avgNotifyMin={8} timely={true} />);
    expect(container.textContent).toContain("Incident Comms");
    expect(container.textContent).toContain("2 not communicated");
}); });
