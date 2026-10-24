import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiCompliancePanel } from "@/components/fleet-ai-compliance-panel";
describe("FleetAiCompliancePanel", () => { it("renders", () => {
    const { container } = render(<FleetAiCompliancePanel totalChecks={50} passing={50} regulations={5} audits={20} compliant={true} />);
    expect(container.textContent).toContain("AI Compliance");
    expect(container.textContent).toContain("Fully compliant");
}); });
