import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDependabotPanel } from "@/components/fleet-dependabot-panel";
describe("FleetDependabotPanel", () => { it("renders", () => {
    const { container } = render(<FleetDependabotPanel total={30} enabled={28} securityAlerts={5} autoMerged={50} />);
    expect(container.textContent).toContain("Dependabot");
    expect(container.textContent).toContain("5 security");
}); });
