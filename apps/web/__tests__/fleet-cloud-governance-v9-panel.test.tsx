import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCloudGovernanceV9Panel } from "@/components/fleet-cloud-governance-v9-panel";
describe("FleetCloudGovernanceV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetCloudGovernanceV9Panel rules={50} violations={0} />);
    expect(container.textContent).toContain("Cloud Governance v9");
}); });
