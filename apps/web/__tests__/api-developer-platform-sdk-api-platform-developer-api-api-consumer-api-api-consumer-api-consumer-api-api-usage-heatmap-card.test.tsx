import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-api-usage-heatmap-card";

describe("ConsumerApiUsageHeatmapCard", () => {
  it("shows heatmap", () => {
    const buckets = [{ hour: 10, day: 0, count: 100 }, { hour: 14, day: 2, count: 50 }];
    const { container } = render(<Card buckets={buckets} peakHour={10} peakDay={0} totalRequests={150} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("Usage Heatmap");
    expect(container.textContent).toContain("Mon at 10:00");
    expect(container.textContent).toContain("150");
  });
  it("shows empty", () => {
    const { container } = render(<Card buckets={[]} peakHour={0} peakDay={0} totalRequests={0} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("No usage data");
  });
});
