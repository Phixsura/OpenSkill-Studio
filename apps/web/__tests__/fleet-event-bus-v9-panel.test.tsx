import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetEventBusV9Panel } from "@/components/fleet-event-bus-v9-panel";
describe("FleetEventBusV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetEventBusV9Panel topics={100} eps={200000} />);
    expect(container.textContent).toContain("Event Bus v9");
}); });
