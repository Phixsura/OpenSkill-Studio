import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TimeoutAnalyticsPanel } from "@/components/timeout-analytics-panel";
describe("TimeoutAnalyticsPanel", () => {
  it("renders", () => {
    const { container } = render(
      <TimeoutAnalyticsPanel totalTimeouts={10} totalRequests={200} thresholdMs={5000} overallRate={5}
        endpoints={[{ endpoint: "/api/slow", timeouts: 10, total: 100, timeoutRate: 10 }]} />
    );
    expect(container.textContent).toContain("Timeout Analytics");
    expect(container.textContent).toContain("10 timeouts (5%)");
    expect(container.textContent).toContain("5000ms threshold");
    expect(container.textContent).toContain("/api/slow");
    expect(container.textContent).toContain("10 timeouts (10%)");
  });
});
