import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RateLimitGauge } from "@/components/rate-limit-gauge";

describe("RateLimitGauge", () => {
  it("renders gauges", () => {
    const { container } = render(
      <RateLimitGauge buckets={[
        { key: "api", tokens: 70, capacity: 100, fillPct: 70 },
        { key: "webhooks", tokens: 5, capacity: 50, fillPct: 10 },
      ]} />
    );
    expect(container.textContent).toContain("Rate Limit Buckets");
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("70/100");
    expect(container.textContent).toContain("webhooks");
    expect(container.textContent).toContain("10%");
  });
});
