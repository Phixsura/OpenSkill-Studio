import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDeveloperApiApiConsumerRateLimitStatusCard from "../src/components/api-developer-api-api-developer-api-api-consumer-rate-limit-status-card";

const statuses = [
  { consumer_id: "acme", endpoint: "/api/users", limit: 1000, remaining: 200, usage_pct: 80, throttled: false },
  { consumer_id: "beta", endpoint: "/api/data", limit: 100, remaining: 0, usage_pct: 100, throttled: true },
];

describe("Card", () => {
  it("shows statuses", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiConsumerRateLimitStatusCard statuses={statuses} throttledCount={1} nearLimitCount={1} appName="App" />);
    expect(container.textContent).toContain("Rate Limit Status");
    expect(container.textContent).toContain("1 throttled");
    expect(container.textContent).toContain("1 near limit");
    expect(container.textContent).toContain("200/1000");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiConsumerRateLimitStatusCard statuses={[]} throttledCount={0} nearLimitCount={0} appName="App" />);
    expect(container.textContent).toContain("No rate limit data");
  });
});
