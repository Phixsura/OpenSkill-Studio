import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIPerformanceOverviewCard from "../src/components/api-developer-api-performance-overview-card";

const perf = { avg_latency_ms: 45, p50_ms: 30, p95_ms: 120, p99_ms: 180, total_requests: 1000000, requests_per_second: 5000, error_rate: 0.3, performance_grade: "A", slowest_endpoint: "/api/search" };

describe("APIDeveloperAPIPerformanceOverviewCard", () => {
  it("shows performance", () => {
    const { container } = render(<APIDeveloperAPIPerformanceOverviewCard performance={perf} appName="App" />);
    expect(container.textContent).toContain("Performance");
    expect(container.textContent).toContain("A");
    expect(container.textContent).toContain("45ms");
    expect(container.textContent).toContain("180ms");
    expect(container.textContent).toContain("5,000");
  });
});
