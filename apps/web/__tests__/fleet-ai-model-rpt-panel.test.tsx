import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiModelRptPanel } from "@/components/fleet-ai-model-rpt-panel";
describe("FleetAiModelRptPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiModelRptPanel reporters={3} active={3} reports={500} metrics={1000} stakeholders={200} />);
    expect(container.textContent).toContain("Model Report");
}); });
