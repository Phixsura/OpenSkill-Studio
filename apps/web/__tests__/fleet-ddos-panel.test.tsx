import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDdosPanel } from "@/components/fleet-ddos-panel";
describe("FleetDdosPanel", () => { it("renders", () => {
    const { container } = render(<FleetDdosPanel zones={5} underAttack={1} mitigatedGbps={50} allClear={false} />);
    expect(container.textContent).toContain("DDoS Protection");
    expect(container.textContent).toContain("1 under attack");
}); });
