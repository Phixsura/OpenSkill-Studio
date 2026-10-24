import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetKyvernoPanel } from "@/components/fleet-kyverno-panel";
describe("FleetKyvernoPanel", () => { it("renders", () => {
    const { container } = render(<FleetKyvernoPanel total={20} enforcing={15} audit={5} violations={3} compliant={false} />);
    expect(container.textContent).toContain("Kyverno");
    expect(container.textContent).toContain("Policy violations");
}); });
