import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiAnomalyPanel } from "@/components/fleet-ai-anomaly-panel";
describe("FleetAiAnomalyPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiAnomalyPanel detectors={8} active={8} metrics={50000} anomalies={25} fpRate={1.5} />);
    expect(container.textContent).toContain("Anomaly Detection");
}); });
