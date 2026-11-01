import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCfQueuesPanel } from "@/components/fleet-cf-queues-panel";
describe("FleetCfQueuesPanel", () => { it("renders", () => {
    const { container } = render(<FleetCfQueuesPanel queues={10} active={10} produced={5000000} consumed={4900000} backlog={100000} />);
    expect(container.textContent).toContain("CF Queues");
}); });
