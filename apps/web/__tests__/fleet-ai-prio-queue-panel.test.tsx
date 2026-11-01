import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPrioQueuePanel } from "@/components/fleet-ai-prio-queue-panel";
describe("FleetAiPrioQueuePanel", () => { it("renders", () => {
    const { container } = render(<FleetAiPrioQueuePanel queues={4} active={4} levels={8} promoted={50000} total={5000000} />);
    expect(container.textContent).toContain("Priority Queue");
}); });
