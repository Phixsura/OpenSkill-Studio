import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TokenBucketViz } from "@/components/token-bucket-viz";

describe("TokenBucketViz", () => {
  it("renders", () => {
    const { container } = render(
      <TokenBucketViz refillRate={1.0} buckets={[
        { key: "user-1", tokens: 8, capacity: 10, pctFull: 80 },
        { key: "user-2", tokens: 1, capacity: 10, pctFull: 10 },
      ]} />
    );
    expect(container.textContent).toContain("Token Buckets");
    expect(container.textContent).toContain("1/s refill");
    expect(container.textContent).toContain("2 keys");
    expect(container.textContent).toContain("user-1");
    expect(container.textContent).toContain("8/10");
    expect(container.textContent).toContain("user-2");
    expect(container.textContent).toContain("1/10");
  });
});
