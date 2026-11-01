import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetPrometheusPanel } from "@/components/fleet-prometheus-panel";
describe("FleetPrometheusPanel", () => { it("renders", () => {
    const { container } = render(<FleetPrometheusPanel instances={3} healthy={3} totalSeries={3000000} storageGb={120} allHealthy={true} />);
    expect(container.textContent).toContain("Prometheus");
    expect(container.textContent).toContain("3,000,000");
}); });
