import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCloudComplianceV9Panel } from "@/components/fleet-cloud-compliance-v9-panel";
describe("FleetCloudComplianceV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetCloudComplianceV9Panel benchmarks={10} score={100} />);
    expect(container.textContent).toContain("Cloud Compliance v9");
}); });
