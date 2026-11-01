import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetObservabilityPipelineV9Panel } from "@/components/fleet-observability-pipeline-v9-panel";
describe("FleetObservabilityPipelineV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetObservabilityPipelineV9Panel stages={5} throughput={100000} />);
    expect(container.textContent).toContain("Obs Pipeline v9");
}); });
