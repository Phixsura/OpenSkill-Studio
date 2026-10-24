import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiExecReportV7Panel } from "@/components/fleet-ai-exec-report-v7-panel";
describe("FleetAiExecReportV7Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiExecReportV7Panel reporters={3} active={3} reports={60} stakeholders={200} kpis={100} />);
    expect(container.textContent).toContain("Executive Report v7");
}); });
