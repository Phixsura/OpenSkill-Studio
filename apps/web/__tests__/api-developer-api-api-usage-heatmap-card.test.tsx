import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiUsageHeatmapCard from "../src/components/api-developer-api-api-usage-heatmap-card";

const buckets = [
  { day_of_week: 0, hour: 9, request_count: 100 },
  { day_of_week: 1, hour: 14, request_count: 200 },
];

describe("APIDeveloperAPIApiUsageHeatmapCard", () => {
  it("shows heatmap", () => {
    const { container } = render(<APIDeveloperAPIApiUsageHeatmapCard buckets={buckets} peakHour={{ day_of_week: 1, hour: 14, request_count: 200 }} totalRequests={300} appName="App" />);
    expect(container.textContent).toContain("Usage Heatmap");
    expect(container.textContent).toContain("300 total");
    expect(container.textContent).toContain("Peak: Tue 14:00");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiUsageHeatmapCard buckets={[]} peakHour={null} totalRequests={0} appName="App" />);
    expect(container.textContent).toContain("No usage data");
  });
});
