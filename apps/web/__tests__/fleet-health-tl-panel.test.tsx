import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetHealthTlPanel } from "@/components/fleet-health-tl-panel";
describe("FleetHealthTlPanel", () => { it("renders", () => {
    const { container } = render(<FleetHealthTlPanel snapshots={30} avgScore={85} best={95} worst={70} trend="improving" />);
    expect(container.textContent).toContain("Health Timeline");
    expect(container.textContent).toContain("improving");
}); });
