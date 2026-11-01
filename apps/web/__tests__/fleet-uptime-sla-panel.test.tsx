import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetUptimeSlaPanel } from "@/components/fleet-uptime-sla-panel";
describe("FleetUptimeSlaPanel", () => { it("renders", () => {
    const { container } = render(<FleetUptimeSlaPanel uptimePct={99.99} downtimeMin={4} nines={4} meetsSla={true} />);
    expect(container.textContent).toContain("Uptime SLA");
    expect(container.textContent).toContain("99.99%");
}); });
