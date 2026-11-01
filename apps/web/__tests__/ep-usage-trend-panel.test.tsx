import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { EpUsageTrendPanel } from "@/components/ep-usage-trend-panel";
describe("EpUsageTrendPanel", () => {
  it("renders", () => {
    const { container } = render(
      <EpUsageTrendPanel trends={[
        { endpoint: "/api/users", changePct: 50, recentAvg: 1500 },
        { endpoint: "/api/orders", changePct: -20, recentAvg: 800 },
      ]} />
    );
    expect(container.textContent).toContain("Usage Trends");
    expect(container.textContent).toContain("2 endpoints trending");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("+50%");
    expect(container.textContent).toContain("1,500/period");
    expect(container.textContent).toContain("-20%");
  });
});
