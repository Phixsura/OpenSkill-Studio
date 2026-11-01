import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiAnalyticsPanel } from "@/components/fleet-ai-analytics-panel";
describe("FleetAiAnalyticsPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiAnalyticsPanel dashboards={10} active={10} metrics={500} views={200000} />);
    expect(container.textContent).toContain("AI Analytics");
}); });
