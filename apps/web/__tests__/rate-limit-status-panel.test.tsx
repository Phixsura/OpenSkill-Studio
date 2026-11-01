import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RateLimitStatusPanel } from "@/components/rate-limit-status-panel";

describe("RateLimitStatusPanel", () => {
  const endpoints = [
    { endpoint: "/api/v1/apps", method: "GET", limit: 1000, used: 200, remaining: 800,
      usage_pct: 20, throttled: false, warning: false, reset_in_sec: 60 },
    { endpoint: "/api/v1/search", method: "GET", limit: 100, used: 120, remaining: 0,
      usage_pct: 120, throttled: true, warning: false, reset_in_sec: 45 },
  ];
  it("renders", () => {
    const { container } = render(<RateLimitStatusPanel endpoints={endpoints} overallHealth="critical" />);
    expect(container.textContent).toContain("Rate Limits");
    expect(container.textContent).toContain("critical");
    expect(container.textContent).toContain("/api/v1/apps");
    expect(container.textContent).toContain("Throttled");
    expect(container.textContent).toContain("resets in 45s");
  });
});
