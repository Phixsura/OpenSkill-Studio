import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApigwHealthPanel } from "@/components/fleet-apigw-health-panel";
describe("FleetApigwHealthPanel", () => { it("renders", () => {
    const { container } = render(<FleetApigwHealthPanel gateways={3} healthy={3} totalRps={8000} avgLatency={15} allHealthy={true} />);
    expect(container.textContent).toContain("API Gateway");
    expect(container.textContent).toContain("8,000 rps");
}); });
