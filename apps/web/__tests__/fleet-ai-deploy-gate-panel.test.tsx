import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiDeployGatePanel } from "@/components/fleet-ai-deploy-gate-panel";
describe("FleetAiDeployGatePanel", () => { it("renders", () => {
    const { container } = render(<FleetAiDeployGatePanel gates={4} active={4} evals={200} passed={190} blocked={10} checks={20} />);
    expect(container.textContent).toContain("Deployment Gate");
}); });
