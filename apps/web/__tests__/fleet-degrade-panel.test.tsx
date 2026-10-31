import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDegradePanel } from "@/components/fleet-degrade-panel";
describe("FleetDegradePanel", () => { it("renders", () => {
    const { container } = render(<FleetDegradePanel total={20} degraded={2} withFallback={18} withoutFallback={2} allProtected={false} />);
    expect(container.textContent).toContain("Graceful Degradation");
    expect(container.textContent).toContain("2 without fallback");
}); });
