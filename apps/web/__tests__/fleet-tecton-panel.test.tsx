import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetTectonPanel } from "@/components/fleet-tecton-panel";
describe("FleetTectonPanel", () => { it("renders", () => {
    const { container } = render(<FleetTectonPanel workspaces={3} active={3} features={500} servesPerSec={150000} />);
    expect(container.textContent).toContain("Tecton");
}); });
