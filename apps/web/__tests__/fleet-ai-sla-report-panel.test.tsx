import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiSlaReportPanel } from "@/components/fleet-ai-sla-report-panel";
describe("FleetAiSlaReportPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiSlaReportPanel reporters={3} active={3} reports={200} slos={80} compliance={99.8} />);
    expect(container.textContent).toContain("SLA Reporter");
}); });
