import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RateLimiterStatus } from "@/components/rate-limiter-status";

describe("RateLimiterStatus", () => {
  const endpoints = [
    { path: "/api/apps", limit: 100, remaining: 80, resetSec: 0 },
    { path: "/api/search", limit: 50, remaining: 2, resetSec: 30 },
  ];
  it("renders", () => {
    const { container } = render(<RateLimiterStatus endpoints={endpoints} />);
    expect(container.textContent).toContain("Rate Limiter");
    expect(container.textContent).toContain("/api/apps");
    expect(container.textContent).toContain("80/100");
    expect(container.textContent).toContain("/api/search");
    expect(container.textContent).toContain("Resets in 30s");
  });
});
