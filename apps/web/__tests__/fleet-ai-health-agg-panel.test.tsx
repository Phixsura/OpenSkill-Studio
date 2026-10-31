import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiHealthAggPanel } from "@/components/fleet-ai-health-agg-panel";
describe("FleetAiHealthAggPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiHealthAggPanel aggregators={2} active={2} services={1000} healthy={998} degraded={2} down={0} healthPct={99.8} />);
    expect(container.textContent).toContain("Health Aggregator");
}); });
