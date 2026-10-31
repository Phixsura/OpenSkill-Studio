import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiCompliancePanel } from "@/components/fleet-ai-compliance-panel";
describe("FleetAiCompliancePanel", () => { it("renders", () => {
    const { container } = render(<FleetAiCompliancePanel audits={5} passed={5} failed={0} frameworks={["SOC2", "GDPR"]} />);
    expect(container.textContent).toContain("Compliance");
}); });
