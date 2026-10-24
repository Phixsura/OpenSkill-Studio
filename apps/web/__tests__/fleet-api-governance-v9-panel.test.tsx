import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiGovernanceV9Panel } from "@/components/fleet-api-governance-v9-panel";
describe("FleetApiGovernanceV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiGovernanceV9Panel apis={100} compliant={100} />);
    expect(container.textContent).toContain("API Governance v9");
}); });
