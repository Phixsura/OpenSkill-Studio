import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAnomalyDetPanel } from "@/components/fleet-anomaly-det-panel";
describe("FleetAnomalyDetPanel", () => { it("renders", () => {
    const { container } = render(<FleetAnomalyDetPanel anomalies={2} total={100} mean={50} std={10} />);
    expect(container.textContent).toContain("Anomaly Detection");
    expect(container.textContent).toContain("Anomalies detected");
}); });
