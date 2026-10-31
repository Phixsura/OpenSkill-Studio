import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import UsageForecastCard from "../src/components/api-developer-platform-sdk-consumer-api-usage-forecast-card";

describe("UsageForecastCard", () => {
  it("renders title and metrics", () => {
    const { container } = render(<UsageForecastCard />);
    expect(container.textContent).toContain("Usage Forecast");
    expect(container.textContent).toContain("API Calls");
    expect(container.textContent).toContain("Data Transfer");
  });

  it("shows trends and forecast", () => {
    const { container } = render(<UsageForecastCard />);
    expect(container.textContent).toContain("15%");
    expect(container.textContent).toContain("2 metrics tracked");
  });
});
