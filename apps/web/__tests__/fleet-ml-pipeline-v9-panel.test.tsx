import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetMlPipelineV9Panel } from "@/components/fleet-ml-pipeline-v9-panel";
describe("FleetMlPipelineV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetMlPipelineV9Panel pipelines={10} gpuHours={150} />);
    expect(container.textContent).toContain("ML Pipeline v9");
}); });
