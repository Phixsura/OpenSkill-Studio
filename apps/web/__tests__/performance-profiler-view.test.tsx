import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PerformanceProfilerView } from "@/components/performance-profiler-view";

describe("PerformanceProfilerView", () => {
  const endpoints = [
    { endpoint: "/api/search", method: "GET", p50_ms: 200, p95_ms: 800, p99_ms: 1500, is_slow: true, score: 20 },
    { endpoint: "/api/apps", method: "GET", p50_ms: 30, p95_ms: 80, p99_ms: 150, is_slow: false, score: 92 },
  ];
  it("renders", () => {
    const { container } = render(
      <PerformanceProfilerView endpoints={endpoints} overallScore={85} avgP95Ms={440} slowCount={1} />
    );
    expect(container.textContent).toContain("Performance Profile");
    expect(container.textContent).toContain("85");
    expect(container.textContent).toContain("440ms");
    expect(container.textContent).toContain("⚠ Slow");
    expect(container.textContent).toContain("/api/search");
  });
});
