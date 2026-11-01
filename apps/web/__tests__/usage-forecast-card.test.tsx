import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import UsageForecastCard from "../src/components/usage-forecast-card";

const forecasts = [
  {
    metric: "api_calls",
    current: 8000,
    predicted: 12000,
    trend: "growing" as const,
    days_to_limit: 15,
    growth_rate_per_day: 200,
  },
  {
    metric: "storage_gb",
    current: 50,
    predicted: 52,
    trend: "stable" as const,
    days_to_limit: null,
    growth_rate_per_day: 0.1,
  },
  {
    metric: "error_count",
    current: 100,
    predicted: 50,
    trend: "declining" as const,
    days_to_limit: null,
    growth_rate_per_day: -5,
  },
];

describe("UsageForecastCard", () => {
  it("renders header and app name", () => {
    const { container } = render(<UsageForecastCard forecasts={forecasts} appName="My App" />);
    expect(container.textContent).toContain("Usage Forecast");
    expect(container.textContent).toContain("My App");
  });

  it("shows at-risk badge", () => {
    const { container } = render(<UsageForecastCard forecasts={forecasts} appName="App" />);
    expect(container.textContent).toContain("1 at risk");
  });

  it("renders metric names", () => {
    const { container } = render(<UsageForecastCard forecasts={forecasts} appName="App" />);
    expect(container.textContent).toContain("api calls");
    expect(container.textContent).toContain("storage gb");
  });

  it("shows trend labels", () => {
    const { container } = render(<UsageForecastCard forecasts={forecasts} appName="App" />);
    expect(container.textContent).toContain("growing");
    expect(container.textContent).toContain("stable");
    expect(container.textContent).toContain("declining");
  });

  it("shows days to limit", () => {
    const { container } = render(<UsageForecastCard forecasts={forecasts} appName="App" />);
    expect(container.textContent).toContain("15d to limit");
  });

  it("shows current and predicted", () => {
    const { container } = render(<UsageForecastCard forecasts={forecasts} appName="App" />);
    expect(container.textContent).toContain("8.0K");
    expect(container.textContent).toContain("12.0K");
  });

  it("shows empty state", () => {
    const { container } = render(<UsageForecastCard forecasts={[]} appName="App" />);
    expect(container.textContent).toContain("No forecasts available");
  });
});
