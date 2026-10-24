import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetWoodpeckerPanel } from "@/components/fleet-woodpecker-panel";
describe("FleetWoodpeckerPanel", () => { it("renders", () => {
    const { container } = render(<FleetWoodpeckerPanel total={20} success={18} failed={2} avgSec={90} />);
    expect(container.textContent).toContain("Woodpecker CI");
}); });
