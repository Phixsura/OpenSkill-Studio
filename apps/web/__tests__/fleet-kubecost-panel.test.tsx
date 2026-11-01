import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetKubecostPanel } from "@/components/fleet-kubecost-panel";
describe("FleetKubecostPanel", () => { it("renders", () => {
    const { container } = render(<FleetKubecostPanel clusters={3} monthlyCost={30000} savingsAvailable={5000} savingsPct={16.7} />);
    expect(container.textContent).toContain("Kubecost");
    expect(container.textContent).toContain("$5,000 savings");
}); });
