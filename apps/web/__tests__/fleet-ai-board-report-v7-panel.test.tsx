import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiBoardReportV7Panel } from "@/components/fleet-ai-board-report-v7-panel";
describe("FleetAiBoardReportV7Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiBoardReportV7Panel reports={2} active={2} quarterly={8} metrics={50} revenue={500000000} />);
    expect(container.textContent).toContain("Board Report v7");
}); });
