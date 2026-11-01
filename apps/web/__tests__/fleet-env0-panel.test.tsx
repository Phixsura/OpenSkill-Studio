import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetEnv0Panel } from "@/components/fleet-env0-panel";
describe("FleetEnv0Panel", () => { it("renders", () => {
    const { container } = render(<FleetEnv0Panel total={20} active={15} monthlyCost={5000} ttlEnforced={12} />);
    expect(container.textContent).toContain("env0");
    expect(container.textContent).toContain("$5,000/mo");
}); });
