import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AppAnalyticsOverview } from "@/components/app-analytics-overview";

describe("AppAnalyticsOverview", () => {
  it("renders analytics", () => {
    const { container } = render(
      <AppAnalyticsOverview appId="myapp" netDisplay="+950" apiDisplay="500,000"
        activeUsers={800} retentionPct={80} errorRate={0.02}
        avgResponseMs={85} rating={4.5} reviews={120} health="excellent" />
    );
    expect(container.textContent).toContain("App Analytics");
    expect(container.textContent).toContain("+950");
    expect(container.textContent).toContain("500,000");
    expect(container.textContent).toContain("800");
    expect(container.textContent).toContain("4.5");
    expect(container.textContent).toContain("excellent");
    expect(container.textContent).toContain("80%");
  });
});
