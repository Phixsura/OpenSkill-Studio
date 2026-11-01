import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiTrainSchedPanel } from "@/components/fleet-ai-train-sched-panel";
describe("FleetAiTrainSchedPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiTrainSchedPanel schedulers={4} active={4} queued={30} running={80} completed={500} avgWait={3} />);
    expect(container.textContent).toContain("Training Scheduler");
}); });
