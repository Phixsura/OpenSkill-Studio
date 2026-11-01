import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetTrafficPolicyV9Panel } from "@/components/fleet-traffic-policy-v9-panel";
describe("FleetTrafficPolicyV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetTrafficPolicyV9Panel policies={30} active={30} />);
    expect(container.textContent).toContain("Traffic Policy v9");
}); });
