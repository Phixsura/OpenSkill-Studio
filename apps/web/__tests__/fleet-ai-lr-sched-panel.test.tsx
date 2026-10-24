import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiLrSchedPanel } from "@/components/fleet-ai-lr-sched-panel";
describe("FleetAiLrSchedPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiLrSchedPanel schedulers={3} active={3} jobs={200} strategies={["cosine", "warmup"]} adjustments={10000} />);
    expect(container.textContent).toContain("LR Scheduler");
}); });
