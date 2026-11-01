import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetLokiPanel } from "@/components/fleet-loki-panel";
describe("FleetLokiPanel", () => { it("renders", () => {
    const { container } = render(<FleetLokiPanel instances={3} healthy={3} ingestionRate={100} queryAvg={150} allHealthy={true} />);
    expect(container.textContent).toContain("Loki");
    expect(container.textContent).toContain("100MB/s");
}); });
