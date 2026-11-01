import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetQwikPanel } from "@/components/fleet-qwik-panel";
describe("FleetQwikPanel", () => { it("renders", () => {
    const { container } = render(<FleetQwikPanel apps={5} deployed={5} routes={200} avgTtfb={40} />);
    expect(container.textContent).toContain("Qwik");
    expect(container.textContent).toContain("40ms TTFB");
}); });
