import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetComplianceScannerV9Panel } from "@/components/fleet-compliance-scanner-v9-panel";
describe("FleetComplianceScannerV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetComplianceScannerV9Panel checks={500} frameworks={5} />);
    expect(container.textContent).toContain("Compliance Scanner v9");
}); });
