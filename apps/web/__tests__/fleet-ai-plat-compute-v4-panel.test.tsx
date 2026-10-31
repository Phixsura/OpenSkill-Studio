import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPlatComputeV4Panel } from "@/components/fleet-ai-plat-compute-v4-panel";
describe("FleetAiPlatComputeV4Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiPlatComputeV4Panel clusters={10} active={10} nodes={10000} gpus={50000} tflops={50000000} />);
    expect(container.textContent).toContain("AI Compute v4");
}); });
