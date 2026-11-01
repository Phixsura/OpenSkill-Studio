import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiBatchSchedPanel } from "@/components/fleet-ai-batch-sched-panel";
describe("FleetAiBatchSchedPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiBatchSchedPanel schedulers={5} active={5} batches={1000} items={200000000} utilization={92} />);
    expect(container.textContent).toContain("Batch Scheduler");
}); });
