import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAnomalyDetectorV9Panel } from "@/components/fleet-anomaly-detector-v9-panel";
describe("FleetAnomalyDetectorV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetAnomalyDetectorV9Panel detectors={10} anomalies={100} />);
    expect(container.textContent).toContain("Anomaly Detector v9");
}); });
