import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDramatiqPanel } from "@/components/fleet-dramatiq-panel";
describe("FleetDramatiqPanel", () => { it("renders", () => {
    const { container } = render(<FleetDramatiqPanel brokers={5} online={5} messages={500000} workers={50} />);
    expect(container.textContent).toContain("Dramatiq");
    expect(container.textContent).toContain("500,000");
}); });
