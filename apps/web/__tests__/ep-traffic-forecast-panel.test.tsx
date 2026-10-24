import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { EpTrafficForecastPanel } from "@/components/ep-traffic-forecast-panel";
describe("EpTrafficForecastPanel", () => {
  it("renders", () => {
    const { container } = render(
      <EpTrafficForecastPanel endpoint="/api/users" trend="growing" currentRps={200} growthRate={15}
        forecast={[{ day: 1, projectedRps: 204 }, { day: 7, projectedRps: 230 }]} />
    );
    expect(container.textContent).toContain("Traffic Forecast: /api/users");
    expect(container.textContent).toContain("growing");
    expect(container.textContent).toContain("200 rps");
    expect(container.textContent).toContain("+15%");
    expect(container.textContent).toContain("+1d");
    expect(container.textContent).toContain("204 rps");
  });
});
