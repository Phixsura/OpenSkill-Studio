import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RateLimitStatus } from "@/components/rate-limit-status";

describe("RateLimitStatus", () => {
  it("renders limits", () => {
    const { container } = render(
      <RateLimitStatus policies={[
        { name: "API", limit: 100, remaining: 80, retryAfter: 0 },
        { name: "Webhooks", limit: 50, remaining: 0, retryAfter: 30 },
      ]} />
    );
    expect(container.textContent).toContain("Rate Limits");
    expect(container.textContent).toContain("API");
    expect(container.textContent).toContain("80/100");
    expect(container.textContent).toContain("Webhooks");
    expect(container.textContent).toContain("retry in 30s");
  });
});
