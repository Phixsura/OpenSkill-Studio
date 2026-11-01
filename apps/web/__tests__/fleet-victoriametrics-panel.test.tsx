import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetVictoriametricsPanel } from "@/components/fleet-victoriametrics-panel";
describe("FleetVictoriametricsPanel", () => { it("renders", () => {
    const { container } = render(<FleetVictoriametricsPanel nodes={6} healthy={6} rowsPerSec={3000000} storageGb={2000} />);
    expect(container.textContent).toContain("VictoriaMetrics");
    expect(container.textContent).toContain("3,000,000");
}); });
