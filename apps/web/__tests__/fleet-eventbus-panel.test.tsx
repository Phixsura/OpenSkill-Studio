import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetEventbusPanel } from "@/components/fleet-eventbus-panel";
describe("FleetEventbusPanel", () => { it("renders", () => {
    const { container } = render(<FleetEventbusPanel totalEps={3000} maxLag={6000} topics={5} lagging={true} />);
    expect(container.textContent).toContain("Fleet Event Bus");
    expect(container.textContent).toContain("Consumer lag");
}); });
