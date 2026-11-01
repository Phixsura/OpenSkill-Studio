import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCompliancePanel } from "@/components/fleet-compliance-panel";
describe("FleetCompliancePanel", () => { it("renders", () => {
    const { container } = render(<FleetCompliancePanel score={90} grade="A" passing={9} failing={1} />);
    expect(container.textContent).toContain("Compliance");
    expect(container.textContent).toContain("90% — A");
}); });
