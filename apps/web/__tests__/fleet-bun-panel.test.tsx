import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetBunPanel } from "@/components/fleet-bun-panel";
describe("FleetBunPanel", () => { it("renders", () => {
    const { container } = render(<FleetBunPanel apps={5} running={5} rps={1000000} avgStartup={8} />);
    expect(container.textContent).toContain("Bun");
    expect(container.textContent).toContain("1,000,000");
}); });
