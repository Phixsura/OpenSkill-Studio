import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDeploymentAuditV9Panel } from "@/components/fleet-deployment-audit-v9-panel";
describe("FleetDeploymentAuditV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetDeploymentAuditV9Panel deploys={500} approved={500} />);
    expect(container.textContent).toContain("Deploy Audit v9");
}); });
