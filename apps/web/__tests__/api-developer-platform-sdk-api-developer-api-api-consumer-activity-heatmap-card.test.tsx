import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiDeveloperApiApiConsumerActivityHeatmapCard from "../src/components/api-developer-platform-sdk-api-developer-api-api-consumer-activity-heatmap-card";

const maps = [{ consumer_id: "acme", total_activity: 50000, peak_hour: 14, peak_day: 2 }];

describe("Card", () => {
  it("shows activity heatmap", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiDeveloperApiApiConsumerActivityHeatmapCard maps={maps} appName="App" />);
    expect(container.textContent).toContain("Activity Heatmap");
    expect(container.textContent).toContain("acme");
    expect(container.textContent).toContain("50,000");
    expect(container.textContent).toContain("14:00 Wed");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiDeveloperApiApiConsumerActivityHeatmapCard maps={[]} appName="App" />);
    expect(container.textContent).toContain("No activity data");
  });
});
