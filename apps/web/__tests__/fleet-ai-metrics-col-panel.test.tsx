import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiMetricsColPanel } from "@/components/fleet-ai-metrics-col-panel";
describe("FleetAiMetricsColPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiMetricsColPanel collectors={5} active={5} metrics={5000000000} series={100000} resolution={1} />);
    expect(container.textContent).toContain("Metrics Collector");
}); });
