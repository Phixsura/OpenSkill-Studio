import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiVerPanel } from "@/components/fleet-api-ver-panel";
describe("FleetApiVerPanel", () => { it("renders", () => {
    const { container } = render(<FleetApiVerPanel total={10} deprecated={2} needsMigration={true} />);
    expect(container.textContent).toContain("API Versions");
    expect(container.textContent).toContain("2 deprecated");
}); });
