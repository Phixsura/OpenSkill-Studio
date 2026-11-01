import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiMsgQueuePanel } from "@/components/fleet-ai-msg-queue-panel";
describe("FleetAiMsgQueuePanel", () => { it("renders", () => {
    const { container } = render(<FleetAiMsgQueuePanel queues={6} active={6} messages={500000000} dlq={0} latency={3} />);
    expect(container.textContent).toContain("Message Queue");
}); });
