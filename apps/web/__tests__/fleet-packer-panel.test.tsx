import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetPackerPanel } from "@/components/fleet-packer-panel";
describe("FleetPackerPanel", () => { it("renders", () => {
    const { container } = render(<FleetPackerPanel total={10} succeeded={9} failed={1} avgDuration={18} />);
    expect(container.textContent).toContain("Packer");
}); });
