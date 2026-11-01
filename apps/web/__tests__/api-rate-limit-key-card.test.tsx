import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIRateLimitKeyCard from "../src/components/api-rate-limit-key-card";

const keys = [
  { key_id: "k1", strategy: "ip", identifier: "10.0.0.1", remaining: 80, limit: 100, exhausted: false },
  { key_id: "k2", strategy: "api_key", identifier: "key-abc", remaining: 0, limit: 50, exhausted: true },
];

describe("APIRateLimitKeyCard", () => {
  it("shows keys and exhausted count", () => {
    const { container } = render(<APIRateLimitKeyCard keys={keys} appName="App" />);
    expect(container.textContent).toContain("Rate Limit Keys");
    expect(container.textContent).toContain("1 exhausted");
    expect(container.textContent).toContain("ip");
    expect(container.textContent).toContain("80/100");
  });
  it("shows empty", () => {
    const { container } = render(<APIRateLimitKeyCard keys={[]} appName="App" />);
    expect(container.textContent).toContain("No rate limit keys");
  });
});
