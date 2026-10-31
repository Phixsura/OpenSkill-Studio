import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetNuxtPanel } from "@/components/fleet-nuxt-panel";
describe("FleetNuxtPanel", () => { it("renders", () => {
    const { container } = render(<FleetNuxtPanel apps={8} deployed={8} pages={300} presets={3} />);
    expect(container.textContent).toContain("Nuxt");
    expect(container.textContent).toContain("300 pages");
}); });
