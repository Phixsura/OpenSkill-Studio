import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCortexPanel } from "@/components/fleet-cortex-panel";
describe("FleetCortexPanel", () => { it("renders", () => {
    const { container } = render(<FleetCortexPanel clusters={3} healthy={3} activeSeries={30000000} ingestionRate={1500000} />);
    expect(container.textContent).toContain("Cortex");
    expect(container.textContent).toContain("30,000,000");
}); });
