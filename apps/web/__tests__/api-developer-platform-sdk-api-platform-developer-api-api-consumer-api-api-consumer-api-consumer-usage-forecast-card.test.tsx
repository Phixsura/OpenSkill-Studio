import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-usage-forecast-card";

describe("ConsumerUsageForecastCard", () => {
  it("shows forecast", () => {
    const history = [{ period: "2026-01", requests: 1000 }, { period: "2026-02", requests: 1500 }];
    const { container } = render(<Card consumerId="c1" history={history} predictedRequests={2000} nextPeriod="2026-03" trend="increasing" confidence={0.8} growthRate={50} appName="App" />);
    expect(container.textContent).toContain("Usage Forecast");
    expect(container.textContent).toContain("increasing");
    expect(container.textContent).toContain("+50%");
    expect(container.textContent).toContain("80%");
  });
  it("shows predicted count", () => {
    const { container } = render(<Card consumerId="c1" history={[]} predictedRequests={500} nextPeriod="2026-02" trend="stable" confidence={0.3} growthRate={0} appName="App" />);
    expect(container.textContent).toContain("500");
    expect(container.textContent).toContain("stable");
  });
});
