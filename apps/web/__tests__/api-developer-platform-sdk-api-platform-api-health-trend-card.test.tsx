import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiPlatformApiHealthTrendCard from "../src/components/api-developer-platform-sdk-api-platform-api-health-trend-card";

const dataPoints = [{ timestamp: "2025-01-01", health_score: 100, uptime_pct: 99.99, error_rate_pct: 0.1, avg_latency_ms: 45 }];

describe("Card", () => {
  it("shows health trend", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiPlatformApiHealthTrendCard dataPoints={dataPoints} latestScore={100} avgScore={98.5} appName="App" />);
    expect(container.textContent).toContain("Health Trend");
    expect(container.textContent).toContain("avg: 98.5");
    expect(container.textContent).toContain("100");
    expect(container.textContent).toContain("2025-01-01");
    expect(container.textContent).toContain("99.99%");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiPlatformApiHealthTrendCard dataPoints={[]} latestScore={100} avgScore={100} appName="App" />);
    expect(container.textContent).toContain("No health trend data");
  });
});
