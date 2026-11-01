import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetNomadPanel } from "@/components/fleet-nomad-panel";
describe("FleetNomadPanel", () => { it("renders", () => {
    const { container } = render(<FleetNomadPanel total={20} running={18} dead={1} pending={1} />);
    expect(container.textContent).toContain("Nomad");
    expect(container.textContent).toContain("1 dead");
}); });
