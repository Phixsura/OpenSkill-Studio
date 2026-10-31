import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetLitmusPanel } from "@/components/fleet-litmus-panel";
describe("FleetLitmusPanel", () => { it("renders", () => {
    const { container } = render(<FleetLitmusPanel total={20} passed={16} failed={4} resilience={80} resilient={true} />);
    expect(container.textContent).toContain("LitmusChaos");
    expect(container.textContent).toContain("80% resilient");
}); });
