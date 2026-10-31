import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetMetricPipelineV9Panel } from "@/components/fleet-metric-pipeline-v9-panel";
describe("FleetMetricPipelineV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetMetricPipelineV9Panel collectors={10} mps={50000} />);
    expect(container.textContent).toContain("Metric Pipeline v9");
}); });
