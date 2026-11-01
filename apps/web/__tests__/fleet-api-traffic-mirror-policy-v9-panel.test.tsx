import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiTrafficMirrorPolicyV9Panel } from "@/components/fleet-api-traffic-mirror-policy-v9-panel";
describe("FleetApiTrafficMirrorPolicyV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiTrafficMirrorPolicyV9Panel policies={5} mirrored={5000} />);
    expect(container.textContent).toContain("Traffic Mirror Policy v9");
}); });
