import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiAnomalyPanel } from "@/components/fleet-ai-anomaly-panel";
describe("FleetAiAnomalyPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiAnomalyPanel detectors={10} active={10} anomalies={1000} dataPoints={500000000} />);
    expect(container.textContent).toContain("AI Anomaly");
}); });
