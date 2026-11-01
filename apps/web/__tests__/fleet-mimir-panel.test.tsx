import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetMimirPanel } from "@/components/fleet-mimir-panel";
describe("FleetMimirPanel", () => { it("renders", () => {
    const { container } = render(<FleetMimirPanel clusters={2} healthy={2} totalSeries={10000000} samplesPerSec={200000} allHealthy={true} />);
    expect(container.textContent).toContain("Mimir");
    expect(container.textContent).toContain("10,000,000");
}); });
