import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RateLimitStatus } from "@/components/rate-limit-status";

const NORMAL_PROPS = {
  apiKeyPrefix: "osk_app_abc",
  appName: "My Connector",
  windows: [
    { window: "second", max_requests: 10, current: 3, remaining: 7 },
    { window: "minute", max_requests: 500, current: 120, remaining: 380 },
    { window: "hour", max_requests: 5000, current: 4800, remaining: 200 },
  ],
  inPenalty: false,
  penaltyExpiresAt: null,
  totalRequests: 45000,
  totalBlocked: 230,
};

const PENALTY_PROPS = {
  ...NORMAL_PROPS,
  inPenalty: true,
  penaltyExpiresAt: new Date(Date.now() + 30000).toISOString(),
  totalBlocked: 5000,
};

describe("RateLimitStatus", () => {
  it("renders heading and app name", () => {
    const { container } = render(<RateLimitStatus {...NORMAL_PROPS} />);
    expect(container.textContent).toContain("Rate Limits");
    expect(container.textContent).toContain("My Connector");
  });

  it("renders API key prefix", () => {
    const { container } = render(<RateLimitStatus {...NORMAL_PROPS} />);
    expect(container.textContent).toContain("osk_app_abc...");
  });

  it("renders total requests", () => {
    const { container } = render(<RateLimitStatus {...NORMAL_PROPS} />);
    expect(container.textContent).toContain("45,000 requests");
  });

  it("renders block rate", () => {
    const { container } = render(<RateLimitStatus {...NORMAL_PROPS} />);
    expect(container.textContent).toContain("blocked");
  });

  it("renders all window limits", () => {
    const { container } = render(<RateLimitStatus {...NORMAL_PROPS} />);
    expect(container.textContent).toContain("10/sec");
    expect(container.textContent).toContain("500/min");
    expect(container.textContent).toContain("5,000/hr");
  });

  it("renders remaining counts", () => {
    const { container } = render(<RateLimitStatus {...NORMAL_PROPS} />);
    expect(container.textContent).toContain("7 remaining");
    expect(container.textContent).toContain("380 remaining");
    expect(container.textContent).toContain("200 remaining");
  });

  it("renders usage percentages", () => {
    const { container } = render(<RateLimitStatus {...NORMAL_PROPS} />);
    expect(container.textContent).toContain("30%"); // 3/10
    expect(container.textContent).toContain("24%"); // 120/500
    expect(container.textContent).toContain("96%"); // 4800/5000
  });

  it("shows penalty banner when in penalty", () => {
    const { container } = render(<RateLimitStatus {...PENALTY_PROPS} />);
    expect(container.textContent).toContain("penalty active");
    expect(container.textContent).toContain("all requests blocked");
  });

  it("shows penalty expiry countdown", () => {
    const { container } = render(<RateLimitStatus {...PENALTY_PROPS} />);
    expect(container.textContent).toContain("Expires in");
  });

  it("hides penalty banner when not penalized", () => {
    const { container } = render(<RateLimitStatus {...NORMAL_PROPS} />);
    expect(container.textContent).not.toContain("penalty active");
  });

  it("renders zero block rate correctly", () => {
    const props = { ...NORMAL_PROPS, totalRequests: 100, totalBlocked: 0 };
    const { container } = render(<RateLimitStatus {...props} />);
    expect(container.textContent).toContain("0.0% blocked");
  });
});
