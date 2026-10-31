import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiGpuPoolV2Panel } from "@/components/fleet-ai-gpu-pool-v2-panel";
describe("FleetAiGpuPoolV2Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiGpuPoolV2Panel pools={5} active={5} gpus={20000} allocated={17000} queue={100} utilization={85} />);
    expect(container.textContent).toContain("GPU Pool v2");
}); });
