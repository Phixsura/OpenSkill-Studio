import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetMetricsSrvPanel } from "@/components/fleet-metrics-srv-panel";
describe("FleetMetricsSrvPanel", () => { it("renders", () => {
    const { container } = render(<FleetMetricsSrvPanel instances={2} healthy={2} nodesScraped={20} scrapeInterval={15} />);
    expect(container.textContent).toContain("metrics-server");
    expect(container.textContent).toContain("20 nodes");
}); });
