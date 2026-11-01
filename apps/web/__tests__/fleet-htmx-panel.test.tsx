import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetHtmxPanel } from "@/components/fleet-htmx-panel";
describe("FleetHtmxPanel", () => { it("renders", () => {
    const { container } = render(<FleetHtmxPanel apps={10} active={10} swaps={2000000} avgSwap={25} />);
    expect(container.textContent).toContain("HTMX");
    expect(container.textContent).toContain("2,000,000");
}); });
