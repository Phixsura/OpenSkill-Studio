import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-usage-heatmap-card";

describe("UsageHeatmapCard", () => {
  it("shows heatmap info", () => {
    const { container } = render(<Card cells={[]} peakDay="tue" peakHour={14} totalRequests={50000} appName="App" />);
    expect(container.textContent).toContain("Usage Heatmap");
    expect(container.textContent).toContain("50,000 total");
    expect(container.textContent).toContain("Peak: tue 14:00");
  });
  it("shows description", () => {
    const { container } = render(<Card cells={[]} peakDay="mon" peakHour={9} totalRequests={0} appName="App" />);
    expect(container.textContent).toContain("request volume");
  });
});
