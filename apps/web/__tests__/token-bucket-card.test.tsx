import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import TokenBucketCard from "../src/components/token-bucket-card";

const buckets = [
  { bucket_id: "api", capacity: 100, refill_rate: 10, available: 75 },
  { bucket_id: "search", capacity: 50, refill_rate: 5, available: 3 },
];

describe("TokenBucketCard", () => {
  it("renders header and count", () => {
    const { container } = render(<TokenBucketCard buckets={buckets} appName="App" />);
    expect(container.textContent).toContain("Token Buckets");
    expect(container.textContent).toContain("2 buckets");
  });

  it("shows bucket IDs and tokens", () => {
    const { container } = render(<TokenBucketCard buckets={buckets} appName="App" />);
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("75 / 100 tokens");
  });

  it("shows refill rate", () => {
    const { container } = render(<TokenBucketCard buckets={buckets} appName="App" />);
    expect(container.textContent).toContain("10/s refill");
    expect(container.textContent).toContain("5/s refill");
  });

  it("shows low bucket", () => {
    const { container } = render(<TokenBucketCard buckets={buckets} appName="App" />);
    expect(container.textContent).toContain("3 / 50 tokens");
  });

  it("shows empty state", () => {
    const { container } = render(<TokenBucketCard buckets={[]} appName="App" />);
    expect(container.textContent).toContain("No token buckets");
  });
});
