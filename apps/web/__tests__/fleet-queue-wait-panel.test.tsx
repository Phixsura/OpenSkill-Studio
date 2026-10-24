import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetQueueWaitPanel } from "@/components/fleet-queue-wait-panel";
describe("FleetQueueWaitPanel", () => { it("renders", () => {
    const { container } = render(<FleetQueueWaitPanel services={5} avgWait={150} p99Wait={8000} acceptable={false} />);
    expect(container.textContent).toContain("Queue Wait Time");
    expect(container.textContent).toContain("High queue wait");
}); });
