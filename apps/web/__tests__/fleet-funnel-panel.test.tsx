import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetFunnelPanel } from "@/components/fleet-funnel-panel";
describe("FleetFunnelPanel", () => { it("renders", () => {
    const { container } = render(<FleetFunnelPanel steps={3} overallRate={30} worstDrop={{ step: "signup", drop_pct: 50 }} healthy={true} />);
    expect(container.textContent).toContain("Conversion Funnel");
    expect(container.textContent).toContain("30% conversion");
}); });
