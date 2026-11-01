import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSupportPanel } from "@/components/fleet-support-panel";
describe("FleetSupportPanel", () => { it("renders", () => {
    const { container } = render(<FleetSupportPanel total={100} open={10} resolved={90} avgResolution={6} backlogHealthy={true} />);
    expect(container.textContent).toContain("Support Tickets");
    expect(container.textContent).toContain("10 open");
}); });
