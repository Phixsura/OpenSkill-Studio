import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiTaskSchedPanel } from "@/components/fleet-ai-task-sched-panel";
describe("FleetAiTaskSchedPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiTaskSchedPanel schedulers={4} active={4} tasks={1000} executions={200000} failures={0} />);
    expect(container.textContent).toContain("Task Scheduler");
}); });
