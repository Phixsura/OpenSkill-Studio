import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetMixpanelPanel } from "@/components/fleet-mixpanel-panel";
describe("FleetMixpanelPanel", () => { it("renders", () => {
    const { container } = render(<FleetMixpanelPanel projects={5} active={5} events={25000000} users={500000} />);
    expect(container.textContent).toContain("Mixpanel");
}); });
