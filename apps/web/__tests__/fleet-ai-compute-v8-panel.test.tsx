import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiComputeV8Panel } from "@/components/fleet-ai-compute-v8-panel";
describe("FleetAiComputeV8Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiComputeV8Panel clusters={10} active={10} nodes={100000} gpus={500000} tflops={500000000} utilization={90} />);
    expect(container.textContent).toContain("Compute v8");
}); });
