import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetTempoPanel } from "@/components/fleet-tempo-panel";
describe("FleetTempoPanel", () => { it("renders", () => {
    const { container } = render(<FleetTempoPanel instances={3} healthy={3} tracesPerSec={15000} minRetention={14} allHealthy={true} />);
    expect(container.textContent).toContain("Tempo");
    expect(container.textContent).toContain("15,000");
}); });
