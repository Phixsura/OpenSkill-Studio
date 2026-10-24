import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetGoldilocksPanel } from "@/components/fleet-goldilocks-panel";
describe("FleetGoldilocksPanel", () => { it("renders", () => {
    const { container } = render(<FleetGoldilocksPanel total={20} enabled={15} recommendations={200} />);
    expect(container.textContent).toContain("Goldilocks");
    expect(container.textContent).toContain("200 recommendations");
}); });
