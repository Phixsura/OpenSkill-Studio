import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiNodeSchedPanel } from "@/components/fleet-ai-node-sched-panel";
describe("FleetAiNodeSchedPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiNodeSchedPanel schedulers={4} active={4} nodes={2000} placements={100000} preemptions={3} />);
    expect(container.textContent).toContain("Node Scheduler");
}); });
