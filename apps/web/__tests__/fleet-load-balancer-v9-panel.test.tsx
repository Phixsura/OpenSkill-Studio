import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetLoadBalancerV9Panel } from "@/components/fleet-load-balancer-v9-panel";
describe("FleetLoadBalancerV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetLoadBalancerV9Panel pools={10} connections={50000} />);
    expect(container.textContent).toContain("Load Balancer v9");
}); });
