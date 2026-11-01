import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiForecastPanel } from "@/components/fleet-ai-forecast-panel";
describe("FleetAiForecastPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiForecastPanel models={10} active={10} predictions={5000000} mape={4} />);
    expect(container.textContent).toContain("AI Forecasting");
}); });
