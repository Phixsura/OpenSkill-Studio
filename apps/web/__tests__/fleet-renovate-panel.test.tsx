import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetRenovatePanel } from "@/components/fleet-renovate-panel";
describe("FleetRenovatePanel", () => { it("renders", () => {
    const { container } = render(<FleetRenovatePanel total={30} enabled={28} openPrs={15} merged={100} />);
    expect(container.textContent).toContain("Renovate");
    expect(container.textContent).toContain("100 merged");
}); });
