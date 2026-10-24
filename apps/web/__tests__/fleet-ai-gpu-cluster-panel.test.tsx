import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiGpuClusterPanel } from "@/components/fleet-ai-gpu-cluster-panel";
describe("FleetAiGpuClusterPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiGpuClusterPanel clusters={5} active={5} gpus={5000} utilized={4200} utilization={84} tflops={2500000} />);
    expect(container.textContent).toContain("GPU Cluster");
}); });
