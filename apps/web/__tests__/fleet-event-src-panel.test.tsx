import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetEventSrcPanel } from "@/components/fleet-event-src-panel";
describe("FleetEventSrcPanel", () => { it("renders", () => {
    const { container } = render(<FleetEventSrcPanel stores={5} totalEvents={5000000} snapshots={500} avgReplay={300} fast={true} />);
    expect(container.textContent).toContain("Event Sourcing");
    expect(container.textContent).toContain("5,000,000 events");
}); });
