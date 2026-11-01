import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiAccessPolicyV9Panel } from "@/components/fleet-api-access-policy-v9-panel";
describe("FleetApiAccessPolicyV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiAccessPolicyV9Panel policies={50} enforced={50} />);
    expect(container.textContent).toContain("API Access Policy v9");
}); });
