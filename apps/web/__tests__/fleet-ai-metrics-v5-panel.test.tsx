import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiMetricsV5Panel } from "@/components/fleet-ai-metrics-v5-panel";
describe("FleetAiMetricsV5Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiMetricsV5Panel collectors={5} active={5} metrics={20000000000} series={1000000} cardinality={5000000} resolution={1} />);
    expect(container.textContent).toContain("AI Metrics v5");
}); });
