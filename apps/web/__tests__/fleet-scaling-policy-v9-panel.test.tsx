import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetScalingPolicyV9Panel } from "@/components/fleet-scaling-policy-v9-panel";
describe("FleetScalingPolicyV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetScalingPolicyV9Panel policies={20} scaleUps={10} />);
    expect(container.textContent).toContain("Scaling Policy v9");
}); });
