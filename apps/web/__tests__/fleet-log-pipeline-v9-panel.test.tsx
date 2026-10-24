import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetLogPipelineV9Panel } from "@/components/fleet-log-pipeline-v9-panel";
describe("FleetLogPipelineV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetLogPipelineV9Panel rate={18000} dropped={0} />);
    expect(container.textContent).toContain("Log Pipeline v9");
}); });
