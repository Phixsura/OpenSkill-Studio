import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TokenBucketGauge } from "@/components/token-bucket-gauge";

describe("TokenBucketGauge", () => {
  it("renders bucket", () => {
    const { container } = render(
      <TokenBucketGauge tokens={50} capacity={100} refillRate={10} fillPct={50} />
    );
    expect(container.textContent).toContain("Token Bucket");
    expect(container.textContent).toContain("50");
    expect(container.textContent).toContain("/100");
    expect(container.textContent).toContain("50%");
    expect(container.textContent).toContain("10 tokens/sec");
  });
});
