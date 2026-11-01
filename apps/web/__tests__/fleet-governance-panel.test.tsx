import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetGovernancePanel } from "@/components/fleet-governance-panel";
describe("FleetGovernancePanel", () => { it("renders", () => {
    const { container } = render(<FleetGovernancePanel total={20} enforced={18} compliancePct={90} fullyGoverned={false} />);
    expect(container.textContent).toContain("Governance");
    expect(container.textContent).toContain("90%");
}); });
