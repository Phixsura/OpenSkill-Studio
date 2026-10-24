import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSreMetricsPanel } from "@/components/fleet-sre-metrics-panel";
describe("FleetSreMetricsPanel", () => { it("renders", () => {
    const { container } = render(<FleetSreMetricsPanel toilPct={20} errorBudgetPct={60} onCallHappiness={4.5} sreMature={true} />);
    expect(container.textContent).toContain("SRE Metrics");
    expect(container.textContent).toContain("SRE Mature");
}); });
