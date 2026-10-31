import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiAnalyticsV7Panel } from "@/components/fleet-ai-analytics-v7-panel";
describe("FleetAiAnalyticsV7Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiAnalyticsV7Panel dashboards={5} active={5} events={50000000000} insights={5000} reports={2000} />);
    expect(container.textContent).toContain("Analytics v7");
}); });
