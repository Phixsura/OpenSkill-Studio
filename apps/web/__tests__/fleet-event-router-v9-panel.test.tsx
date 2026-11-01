import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetEventRouterV9Panel } from "@/components/fleet-event-router-v9-panel";
describe("FleetEventRouterV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetEventRouterV9Panel routes={20} eps={100000} />);
    expect(container.textContent).toContain("Event Router v9");
}); });
