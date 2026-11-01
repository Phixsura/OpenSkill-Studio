import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetNetpolPanel } from "@/components/fleet-netpol-panel";
describe("FleetNetpolPanel", () => { it("renders", () => {
    const { container } = render(<FleetNetpolPanel total={5} covered={3} uncovered={2} fullCoverage={false} />);
    expect(container.textContent).toContain("Network Policies");
    expect(container.textContent).toContain("2/5 without");
}); });
