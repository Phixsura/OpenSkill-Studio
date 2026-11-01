import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetHyperdrivePanel } from "@/components/fleet-hyperdrive-panel";
describe("FleetHyperdrivePanel", () => { it("renders", () => {
    const { container } = render(<FleetHyperdrivePanel configs={5} active={5} cacheHitRate={80} queries={50000000} />);
    expect(container.textContent).toContain("Hyperdrive");
}); });
