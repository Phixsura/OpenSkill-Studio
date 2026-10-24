import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiComplianceCheckV9Panel } from "@/components/fleet-api-compliance-check-v9-panel";
describe("FleetApiComplianceCheckV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiComplianceCheckV9Panel checks={100} passed={100} />);
    expect(container.textContent).toContain("API Compliance Check v9");
}); });
