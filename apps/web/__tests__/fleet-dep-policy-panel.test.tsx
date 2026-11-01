import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDepPolicyPanel } from "@/components/fleet-dep-policy-panel";
describe("FleetDepPolicyPanel", () => { it("renders", () => {
    const { container } = render(<FleetDepPolicyPanel total={10} autoUpdate={8} modern={false} />);
    expect(container.textContent).toContain("Dep Update Policy");
    expect(container.textContent).toContain("Not all");
}); });
