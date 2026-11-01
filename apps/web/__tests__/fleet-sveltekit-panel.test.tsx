import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSveltekitPanel } from "@/components/fleet-sveltekit-panel";
describe("FleetSveltekitPanel", () => { it("renders", () => {
    const { container } = render(<FleetSveltekitPanel apps={5} deployed={5} routes={200} ssrPct={85} />);
    expect(container.textContent).toContain("SvelteKit");
    expect(container.textContent).toContain("85% SSR");
}); });
