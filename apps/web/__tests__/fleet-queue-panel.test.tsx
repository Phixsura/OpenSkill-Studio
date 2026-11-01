import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetQueuePanel } from "@/components/fleet-queue-panel";
describe("FleetQueuePanel", () => { it("renders", () => {
    const { container } = render(<FleetQueuePanel totalDepth={12000} maxDepth={5000} queues={3} backlog={true} />);
    expect(container.textContent).toContain("Fleet Queues");
    expect(container.textContent).toContain("Queue backlog");
}); });
