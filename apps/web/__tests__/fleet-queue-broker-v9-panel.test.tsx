import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetQueueBrokerV9Panel } from "@/components/fleet-queue-broker-v9-panel";
describe("FleetQueueBrokerV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetQueueBrokerV9Panel queues={30} throughput={50000} />);
    expect(container.textContent).toContain("Queue Broker v9");
}); });
