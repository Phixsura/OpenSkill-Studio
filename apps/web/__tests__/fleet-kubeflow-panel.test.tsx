import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetKubeflowPanel } from "@/components/fleet-kubeflow-panel";
describe("FleetKubeflowPanel", () => { it("renders", () => {
    const { container } = render(<FleetKubeflowPanel clusters={3} healthy={3} pipelines={100} notebooks={50} experiments={200} />);
    expect(container.textContent).toContain("Kubeflow");
}); });
