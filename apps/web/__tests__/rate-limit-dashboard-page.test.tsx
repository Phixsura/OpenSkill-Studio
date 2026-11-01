import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RateLimitDashboardPage } from "@/components/rate-limit-dashboard-page";

describe("RateLimitDashboardPage", () => {
  const eps = [
    { method: "GET", path: "/api/apps", currentRpm: 800, rpmLimit: 1000, usagePct: 80, throttled: false },
    { method: "POST", path: "/api/apps", currentRpm: 1200, rpmLimit: 1000, usagePct: 120, throttled: true },
  ];
  it("renders dashboard", () => {
    const { container } = render(
      <RateLimitDashboardPage endpoints={eps} totalRpm={2000} throttledCount={1}
        planLimit={1000} healthy={false} />
    );
    expect(container.textContent).toContain("Rate Limits");
    expect(container.textContent).toContain("/api/apps");
    expect(container.textContent).toContain("800/1000");
    expect(container.textContent).toContain("1200/1000");
    expect(container.textContent).toContain("1 throttled");
  });
});
