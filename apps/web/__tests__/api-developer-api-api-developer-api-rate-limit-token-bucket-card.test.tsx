import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDeveloperApiRateLimitTokenBucketCard from "../src/components/api-developer-api-api-developer-api-rate-limit-token-bucket-card";

const buckets = [
  { consumer_id: "acme", capacity: 100, tokens: 75, fill_pct: 75, refill_rate: 10 },
  { consumer_id: "beta", capacity: 50, tokens: 5, fill_pct: 10, refill_rate: 2 },
];

describe("APIDeveloperAPIApiDeveloperApiRateLimitTokenBucketCard", () => {
  it("shows token buckets", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiRateLimitTokenBucketCard buckets={buckets} appName="App" />);
    expect(container.textContent).toContain("Token Buckets");
    expect(container.textContent).toContain("acme");
    expect(container.textContent).toContain("75/100");
    expect(container.textContent).toContain("10/s");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiRateLimitTokenBucketCard buckets={[]} appName="App" />);
    expect(container.textContent).toContain("No token buckets");
  });
});
