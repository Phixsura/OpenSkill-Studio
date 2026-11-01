import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiLoadBalancingV9Panel } from "@/components/fleet-api-load-balancing-v9-panel";
describe("FleetApiLoadBalancingV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiLoadBalancingV9Panel lbs={10} rps={500000} />);
    expect(container.textContent).toContain("API Load Balancing v9");
}); });
