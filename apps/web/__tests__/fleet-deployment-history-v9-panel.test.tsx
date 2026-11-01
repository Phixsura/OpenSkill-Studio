import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDeploymentHistoryV9Panel } from "@/components/fleet-deployment-history-v9-panel";
describe("FleetDeploymentHistoryV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetDeploymentHistoryV9Panel deploys={1000} rollbacks={5} />);
    expect(container.textContent).toContain("Deployment History v9");
}); });
