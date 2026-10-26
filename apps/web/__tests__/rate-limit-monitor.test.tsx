import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RateLimitMonitor } from "@/components/rate-limit-monitor";

describe("RateLimitMonitor", () => {
  it("renders limits", () => {
    const limits = [
      { endpoint: "/api/data", max: 100, remaining: 20, window: 60 },
      { endpoint: "/api/upload", max: 10, remaining: 1, window: 60 },
    ];
    const { container } = render(<RateLimitMonitor limits={limits} />);
    expect(container.textContent).toContain("/api/data");
    expect(container.textContent).toContain("20/100");
    expect(container.textContent).toContain("1/10");
  });
  it("shows empty state", () => {
    const { container } = render(<RateLimitMonitor limits={[]} />);
    expect(container.textContent).toContain("No rate limits");
  });
});
