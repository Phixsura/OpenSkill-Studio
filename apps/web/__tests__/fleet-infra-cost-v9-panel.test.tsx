import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetInfraCostV9Panel } from "@/components/fleet-infra-cost-v9-panel";
describe("FleetInfraCostV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetInfraCostV9Panel teams={10} total={80000} />);
    expect(container.textContent).toContain("Infra Cost v9");
}); });
