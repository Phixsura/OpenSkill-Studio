import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDeschedulerPanel } from "@/components/fleet-descheduler-panel";
describe("FleetDeschedulerPanel", () => { it("renders", () => {
    const { container } = render(<FleetDeschedulerPanel totalActions={10} podsEvicted={25} rebalances={5} />);
    expect(container.textContent).toContain("Descheduler");
    expect(container.textContent).toContain("25 evicted");
}); });
