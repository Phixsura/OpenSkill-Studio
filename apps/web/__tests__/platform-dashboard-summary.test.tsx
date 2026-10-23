import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformDashboardSummary } from "@/components/platform-dashboard-summary";

describe("PlatformDashboardSummary", () => {
  it("renders", () => {
    const { container } = render(
      <PlatformDashboardSummary totalApps={500} totalDevelopers={200} totalUsers={50000}
        totalInstalls={250000} mrr={85000} arr={1020000} growthPct={15.5}
        uptimePct={99.95} avgLatencyMs={42} dau={5000} mau={35000}
        retention30d={72.5} status="operational" />
    );
    expect(container.textContent).toContain("Platform Dashboard");
    expect(container.textContent).toContain("🟢 Operational");
    expect(container.textContent).toContain("500");
    expect(container.textContent).toContain("$85,000");
    expect(container.textContent).toContain("99.95%");
    expect(container.textContent).toContain("5,000");
  });
});
