import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiReqQueuePanel } from "@/components/fleet-ai-req-queue-panel";
describe("FleetAiReqQueuePanel", () => { it("renders", () => {
    const { container } = render(<FleetAiReqQueuePanel queues={8} active={8} depth={1000} throughput={200000} avgWait={15} />);
    expect(container.textContent).toContain("Request Queue");
}); });
