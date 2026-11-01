import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RateLimitBadge } from "@/components/rate-limit-badge";

describe("RateLimitBadge", () => {
  it("renders remaining", () => {
    const { container } = render(<RateLimitBadge remaining={80} limit={100} retryAfterS={null} />);
    expect(container.textContent).toContain("80/100");
    expect(container.textContent).toContain("Rate Limit");
  });
  it("shows retry after", () => {
    const { container } = render(<RateLimitBadge remaining={0} limit={100} retryAfterS={2.5} />);
    expect(container.textContent).toContain("retry in 2.5s");
  });
});
