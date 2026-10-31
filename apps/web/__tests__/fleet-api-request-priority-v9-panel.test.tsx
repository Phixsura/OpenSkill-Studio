import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiRequestPriorityV9Panel } from "@/components/fleet-api-request-priority-v9-panel";
describe("FleetApiRequestPriorityV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiRequestPriorityV9Panel queues={5} total={500000} />);
    expect(container.textContent).toContain("Request Priority v9");
}); });
