import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetXpCompPanel } from "@/components/fleet-xp-comp-panel";
describe("FleetXpCompPanel", () => { it("renders", () => {
    const { container } = render(<FleetXpCompPanel total={20} ready={18} notReady={2} managedResources={200} />);
    expect(container.textContent).toContain("Crossplane XRs");
    expect(container.textContent).toContain("2 not ready");
}); });
