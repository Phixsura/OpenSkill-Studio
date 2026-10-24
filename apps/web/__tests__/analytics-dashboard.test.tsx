import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AnalyticsDashboard } from "@/components/analytics-dashboard";

describe("AnalyticsDashboard", () => {
  it("renders analytics", () => {
    const { container } = render(
      <AnalyticsDashboard activeApps={500} displayRequests="50.0M" avgLatencyMs={85}
        errorRatePct={0.5} dailyActiveUsers={12000} displayRevenue="$75,000" health="excellent" />
    );
    expect(container.textContent).toContain("Platform Analytics");
    expect(container.textContent).toContain("excellent");
    expect(container.textContent).toContain("500");
    expect(container.textContent).toContain("50.0M");
    expect(container.textContent).toContain("85ms");
    expect(container.textContent).toContain("12,000");
    expect(container.textContent).toContain("$75,000");
  });
});
