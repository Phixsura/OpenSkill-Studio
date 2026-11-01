import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCompliancePostureV9Panel } from "@/components/fleet-compliance-posture-v9-panel";
describe("FleetCompliancePostureV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetCompliancePostureV9Panel domains={5} score={95} />);
    expect(container.textContent).toContain("Compliance Posture v9");
}); });
