import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-rate-limit-window-card";

describe("RateLimitWindowCard", () => {
  it("shows windows", () => {
    const windows = [{ consumer_id: "c1", endpoint: "/api", remaining: 20, max_requests: 100, usage_pct: 80 }];
    const { container } = render(<Card windows={windows} blockedCount={2} appName="App" />);
    expect(container.textContent).toContain("Rate Limit Windows");
    expect(container.textContent).toContain("2 blocked");
    expect(container.textContent).toContain("c1 → /api");
    expect(container.textContent).toContain("20/100");
  });
  it("shows empty", () => {
    const { container } = render(<Card windows={[]} blockedCount={0} appName="App" />);
    expect(container.textContent).toContain("No rate limits configured");
  });
});
