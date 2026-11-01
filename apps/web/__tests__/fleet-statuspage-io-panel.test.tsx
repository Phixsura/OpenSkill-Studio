import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetStatuspageIoPanel } from "@/components/fleet-statuspage-io-panel";
describe("FleetStatuspageIoPanel", () => { it("renders", () => {
    const { container } = render(<FleetStatuspageIoPanel pages={3} operational={2} degraded={1} activeIncidents={1} />);
    expect(container.textContent).toContain("StatusPage");
}); });
