import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RateLimitDashboard } from "@/components/rate-limit-dashboard";

const mockLimits = [
  { apiKey: "osk_abc...", keyName: "Production", limit: 1000, used: 850, remaining: 150,
    resetAt: "5m", windowSeconds: 60, burstLimit: 20, burstUsed: 5 },
  { apiKey: "osk_xyz...", keyName: "Staging", limit: 500, used: 100, remaining: 400,
    resetAt: "45s", windowSeconds: 60, burstLimit: 10, burstUsed: 1 },
];

describe("RateLimitDashboard", () => {
  it("renders rate limit cards", () => {
    const { container } = render(<RateLimitDashboard limits={mockLimits} />);
    expect(container.textContent).toContain("Rate Limits");
    expect(container.textContent).toContain("Production");
    expect(container.textContent).toContain("Staging");
    expect(container.textContent).toContain("osk_abc...");
  });

  it("shows usage percentages", () => {
    const { container } = render(<RateLimitDashboard limits={mockLimits} />);
    expect(container.textContent).toContain("850");
    expect(container.textContent).toContain("85%");  // 850/1000
    expect(container.textContent).toContain("150");   // remaining
  });

  it("shows burst info", () => {
    const { container } = render(<RateLimitDashboard limits={mockLimits} />);
    expect(container.textContent).toContain("Burst");
    expect(container.textContent).toContain("5 / 20");
  });
});
