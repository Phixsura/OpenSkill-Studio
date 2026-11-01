import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetTelemetryPipelineV9Panel } from "@/components/fleet-telemetry-pipeline-v9-panel";
describe("FleetTelemetryPipelineV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetTelemetryPipelineV9Panel exporters={8} sps={50000} />);
    expect(container.textContent).toContain("Telemetry Pipeline v9");
}); });
