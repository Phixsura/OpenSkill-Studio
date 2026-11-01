import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSpannerPanel } from "@/components/fleet-spanner-panel";
describe("FleetSpannerPanel", () => { it("renders", () => {
    const { container } = render(<FleetSpannerPanel instances={3} ready={3} nodes={9} cpuPct={35} />);
    expect(container.textContent).toContain("Spanner");
}); });
