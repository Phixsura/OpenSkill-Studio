import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDataPipelineV9Panel } from "@/components/fleet-data-pipeline-v9-panel";
describe("FleetDataPipelineV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetDataPipelineV9Panel jobs={50} rows={5000000} />);
    expect(container.textContent).toContain("Data Pipeline v9");
}); });
