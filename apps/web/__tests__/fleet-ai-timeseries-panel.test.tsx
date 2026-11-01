import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiTimeseriesPanel } from "@/components/fleet-ai-timeseries-panel";
describe("FleetAiTimeseriesPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiTimeseriesPanel models={6} active={6} forecasts={2000000} mape={3.2} horizon={180} />);
    expect(container.textContent).toContain("Time Series");
}); });
