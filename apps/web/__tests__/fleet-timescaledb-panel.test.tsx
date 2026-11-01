import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetTimescaledbPanel } from "@/components/fleet-timescaledb-panel";
describe("FleetTimescaledbPanel", () => { it("renders", () => {
    const { container } = render(<FleetTimescaledbPanel instances={3} healthy={3} chunks={15000} compressionRatio={10} />);
    expect(container.textContent).toContain("TimescaleDB");
    expect(container.textContent).toContain("10x compression");
}); });
