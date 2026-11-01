import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetChaosSchedulerV9Panel } from "@/components/fleet-chaos-scheduler-v9-panel";
describe("FleetChaosSchedulerV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetChaosSchedulerV9Panel schedules={10} runs={500} />);
    expect(container.textContent).toContain("Chaos Scheduler v9");
}); });
