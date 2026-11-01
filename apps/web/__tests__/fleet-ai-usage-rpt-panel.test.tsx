import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiUsageRptPanel } from "@/components/fleet-ai-usage-rpt-panel";
describe("FleetAiUsageRptPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiUsageRptPanel reporters={3} active={3} reports={1000} recipients={5000} insights={100} />);
    expect(container.textContent).toContain("Usage Reporter");
}); });
