import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiCircuitV9Panel } from "@/components/fleet-api-circuit-v9-panel";
describe("FleetApiCircuitV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiCircuitV9Panel circuits={50} open={0} />);
    expect(container.textContent).toContain("API Circuit v9");
}); });
