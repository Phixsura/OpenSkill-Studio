import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RateLimitDashboard } from "@/components/rate-limit-dashboard";

describe("RateLimitDashboard", () => {
  it("renders limits", () => {
    const { container } = render(
      <RateLimitDashboard entries={[
        { key: "api_key_1", limit: 100, remaining: 25, blocked: 3, usagePct: 75 },
        { key: "api_key_2", limit: 500, remaining: 490, blocked: 0, usagePct: 2 },
      ]} />
    );
    expect(container.textContent).toContain("Rate Limits");
    expect(container.textContent).toContain("api_key_1");
    expect(container.textContent).toContain("25/100");
    expect(container.textContent).toContain("3 requests blocked");
    expect(container.textContent).toContain("api_key_2");
  });
});
