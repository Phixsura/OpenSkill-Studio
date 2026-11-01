import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetGpuClusterV9Panel } from "@/components/fleet-gpu-cluster-v9-panel";
describe("FleetGpuClusterV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetGpuClusterV9Panel nodes={10} gpus={80} />);
    expect(container.textContent).toContain("GPU Cluster v9");
}); });
