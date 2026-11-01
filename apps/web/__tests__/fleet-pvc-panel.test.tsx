import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetPvcPanel } from "@/components/fleet-pvc-panel";
describe("FleetPvcPanel", () => { it("renders", () => {
    const { container } = render(<FleetPvcPanel total={10} bound={8} pending={1} lost={1} healthy={false} />);
    expect(container.textContent).toContain("PVCs");
    expect(container.textContent).toContain("1 lost");
}); });
