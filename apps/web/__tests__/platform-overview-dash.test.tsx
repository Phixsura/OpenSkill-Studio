import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformOverviewDash } from "@/components/platform-overview-dash";

describe("PlatformOverviewDash", () => {
  it("renders dashboard", () => {
    const { container } = render(
      <PlatformOverviewDash healthScore={95.6} status="healthy"
        apps={{ total: 500, active: 450, healthyPct: 95 }}
        infra={{ services: 50, uptimePct: 99.9, incidents: 2 }}
        users={{ total: 10000, activeToday: 3000, satisfactionPct: 88 }} />
    );
    expect(container.textContent).toContain("95.6");
    expect(container.textContent).toContain("Platform Health Score");
    expect(container.textContent).toContain("healthy");
    expect(container.textContent).toContain("450/500");
    expect(container.textContent).toContain("99.9%");
    expect(container.textContent).toContain("88% satisfaction");
  });
});
