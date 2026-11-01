import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiRiskMgmtV7Panel } from "@/components/fleet-ai-risk-mgmt-v7-panel";
describe("FleetAiRiskMgmtV7Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiRiskMgmtV7Panel systems={3} active={3} risks={200} mitigated={200} score={98} />);
    expect(container.textContent).toContain("Risk Mgmt v7");
}); });
