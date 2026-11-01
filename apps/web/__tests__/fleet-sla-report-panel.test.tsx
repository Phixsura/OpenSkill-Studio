import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSlaReportPanel } from "@/components/fleet-sla-report-panel";
describe("FleetSlaReportPanel", () => { it("renders", () => {
    const { container } = render(<FleetSlaReportPanel month="Oct" uptimePct={99.95} targetPct={99.9} met={true} credits={0} />);
    expect(container.textContent).toContain("SLA Report");
    expect(container.textContent).toContain("99.95%");
}); });
