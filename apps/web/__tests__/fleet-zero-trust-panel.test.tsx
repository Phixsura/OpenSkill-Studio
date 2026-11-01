import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetZeroTrustPanel } from "@/components/fleet-zero-trust-panel";
describe("FleetZeroTrustPanel", () => { it("renders", () => {
    const { container } = render(<FleetZeroTrustPanel total={20} implemented={16} remaining={4} score={80} mature={true} />);
    expect(container.textContent).toContain("Zero Trust");
    expect(container.textContent).toContain("80%");
}); });
