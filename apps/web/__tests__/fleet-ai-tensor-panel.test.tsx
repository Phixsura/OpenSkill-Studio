import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiTensorPanel } from "@/components/fleet-ai-tensor-panel";
describe("FleetAiTensorPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiTensorPanel clusters={8} active={8} tflops={5000000} jobs={200000} utilization={90} />);
    expect(container.textContent).toContain("Tensor Compute");
}); });
