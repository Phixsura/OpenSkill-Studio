import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-rate-limit-token-bucket-card";

describe("TokenBucketCard", () => {
  it("shows buckets", () => {
    const buckets = [{ consumer_id: "c1", endpoint: "/api", capacity: 100, available: 75, refill_rate: 10 }];
    const { container } = render(<Card buckets={buckets} appName="App" />);
    expect(container.textContent).toContain("Token Buckets");
    expect(container.textContent).toContain("c1 → /api");
    expect(container.textContent).toContain("75/100");
  });
  it("shows empty", () => {
    const { container } = render(<Card buckets={[]} appName="App" />);
    expect(container.textContent).toContain("No token buckets");
  });
});
