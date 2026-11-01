import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiUsageForecastCard from "../src/components/api-developer-api-api-usage-forecast-card";

const forecasts = [
  { endpoint: "/api/users", current_daily_avg: 5000, trend: "growing", growth_rate_pct: 15.5, forecast_7d: 5500, forecast_30d: 7000 },
];

describe("APIDeveloperAPIApiUsageForecastCard", () => {
  it("shows forecasts", () => {
    const { container } = render(<APIDeveloperAPIApiUsageForecastCard forecasts={forecasts} appName="App" />);
    expect(container.textContent).toContain("Usage Forecast");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("+15.5%");
    expect(container.textContent).toContain("now: 5000/day");
    expect(container.textContent).toContain("30d: 7000");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiUsageForecastCard forecasts={[]} appName="App" />);
    expect(container.textContent).toContain("No forecast data");
  });
});
