import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetGrafanaPanel } from "@/components/fleet-grafana-panel";
describe("FleetGrafanaPanel", () => { it("renders", () => {
    const { container } = render(<FleetGrafanaPanel total={50} active={40} stale={5} usageRate={80} />);
    expect(container.textContent).toContain("Grafana");
    expect(container.textContent).toContain("5 stale");
}); });
