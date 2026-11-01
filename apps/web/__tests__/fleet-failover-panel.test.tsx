import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetFailoverPanel } from "@/components/fleet-failover-panel";
describe("FleetFailoverPanel", () => { it("renders", () => {
    const { container } = render(<FleetFailoverPanel regions={3} primary={1} standby={2} standbyReady={1} failoverReady={true} />);
    expect(container.textContent).toContain("Failover");
    expect(container.textContent).toContain("Failover ready");
}); });
