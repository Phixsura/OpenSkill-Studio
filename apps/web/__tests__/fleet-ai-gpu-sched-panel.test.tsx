import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiGpuSchedPanel } from "@/components/fleet-ai-gpu-sched-panel";
describe("FleetAiGpuSchedPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiGpuSchedPanel schedulers={3} active={3} gpus={1000} queued={30} utilization={92} />);
    expect(container.textContent).toContain("GPU Scheduler");
}); });
