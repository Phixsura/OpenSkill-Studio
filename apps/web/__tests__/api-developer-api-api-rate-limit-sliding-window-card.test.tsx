import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiRateLimitSlidingWindowCard from "../src/components/api-developer-api-api-rate-limit-sliding-window-card";

const windows = [
  { consumer_id: "acme", endpoint: "/api/users", current: 80, max: 100, remaining: 20, is_limited: false },
  { consumer_id: "beta", endpoint: "/api/data", current: 50, max: 50, remaining: 0, is_limited: true },
];

describe("APIDeveloperAPIApiRateLimitSlidingWindowCard", () => {
  it("shows windows", () => {
    const { container } = render(<APIDeveloperAPIApiRateLimitSlidingWindowCard windows={windows} limitedCount={1} appName="App" />);
    expect(container.textContent).toContain("Sliding Window");
    expect(container.textContent).toContain("1 limited");
    expect(container.textContent).toContain("acme");
    expect(container.textContent).toContain("80/100");
    expect(container.textContent).toContain("50/50");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiRateLimitSlidingWindowCard windows={[]} limitedCount={0} appName="App" />);
    expect(container.textContent).toContain("No rate limits");
  });
});
