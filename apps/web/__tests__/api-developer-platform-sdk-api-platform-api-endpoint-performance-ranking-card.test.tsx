import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiPlatformApiEndpointPerformanceRankingCard from "../src/components/api-developer-platform-sdk-api-platform-api-endpoint-performance-ranking-card";

const endpoints = [
  { endpoint: "/api/users", performance_score: 95, rank_label: "⚡ Fast", avg_latency_ms: 30, p99_latency_ms: 150, error_rate_pct: 0.1 },
  { endpoint: "/api/heavy", performance_score: 30, rank_label: "🐌 Poor", avg_latency_ms: 500, p99_latency_ms: 3000, error_rate_pct: 10 },
];

describe("Card", () => {
  it("shows ranking", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiPlatformApiEndpointPerformanceRankingCard endpoints={endpoints} appName="App" />);
    expect(container.textContent).toContain("Performance Ranking");
    expect(container.textContent).toContain("#1");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("Fast");
    expect(container.textContent).toContain("Poor");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiPlatformApiEndpointPerformanceRankingCard endpoints={[]} appName="App" />);
    expect(container.textContent).toContain("No performance data");
  });
});
