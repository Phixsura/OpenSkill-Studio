import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetComplianceReportV9Panel } from "@/components/fleet-compliance-report-v9-panel";
describe("FleetComplianceReportV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetComplianceReportV9Panel reports={20} findings={0} />);
    expect(container.textContent).toContain("Compliance Report v9");
}); });
