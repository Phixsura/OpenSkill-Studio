import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetStatusPagePanel } from "@/components/fleet-status-page-panel";
describe("FleetStatusPagePanel", () => { it("renders", () => {
    const { container } = render(<FleetStatusPagePanel components={10} operational={9} degraded={1} outage={0} overall="degraded" />);
    expect(container.textContent).toContain("Status Page");
    expect(container.textContent).toContain("DEGRADED");
}); });
