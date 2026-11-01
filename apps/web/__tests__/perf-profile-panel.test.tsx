import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PerfProfilePanel } from "@/components/perf-profile-panel";
describe("PerfProfilePanel", () => {
  it("renders", () => {
    const { container } = render(
      <PerfProfilePanel totalSamples={5000}
        profiles={[
          { endpoint: "/api/users", samples: 3000, avg: 45, p50: 40, p95: 120, p99: 200 },
          { endpoint: "/api/orders", samples: 2000, avg: 150, p50: 100, p95: 500, p99: 800 },
        ]} />
    );
    expect(container.textContent).toContain("Performance Profiler");
    expect(container.textContent).toContain("2 endpoints");
    expect(container.textContent).toContain("5,000 samples");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("avg:45ms");
    expect(container.textContent).toContain("p99:800ms");
  });
});
