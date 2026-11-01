import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ResponseTimeMonitor } from "@/components/response-time-monitor";

describe("ResponseTimeMonitor", () => {
  it("renders monitor", () => {
    const { container } = render(
      <ResponseTimeMonitor overallAvgMs={120} totalSamples={100} slowest="/api/apps"
        endpoints={[
          { endpoint: "/api/users", count: 50, avgMs: 65, p50Ms: 50, p99Ms: 150, status: "fast" },
          { endpoint: "/api/apps", count: 50, avgMs: 180, p50Ms: 120, p99Ms: 600, status: "slow" },
        ]} />
    );
    expect(container.textContent).toContain("Response Times");
    expect(container.textContent).toContain("120ms");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("p99 600ms");
  });
});
