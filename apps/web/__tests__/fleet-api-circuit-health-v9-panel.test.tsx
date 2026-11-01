import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiCircuitHealthV9Panel } from "@/components/fleet-api-circuit-health-v9-panel";
describe("FleetApiCircuitHealthV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiCircuitHealthV9Panel circuits={100} open={0} />);
    expect(container.textContent).toContain("Circuit Health v9");
}); });
