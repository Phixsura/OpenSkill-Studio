import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiDeploymentPipelineV9Panel } from "@/components/fleet-api-deployment-pipeline-v9-panel";
describe("FleetApiDeploymentPipelineV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiDeploymentPipelineV9Panel pipelines={50} success={50} />);
    expect(container.textContent).toContain("Deploy Pipeline v9");
}); });
