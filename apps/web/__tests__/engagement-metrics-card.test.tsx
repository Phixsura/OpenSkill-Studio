import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { EngagementMetricsCard } from "@/components/engagement-metrics-card";

describe("EngagementMetricsCard", () => {
  it("renders engagement", () => {
    const { container } = render(
      <EngagementMetricsCard period="30d" totalEvents={5000} avgDau={150}
        avgWau={500} stickinessPct={30} topActions={[{ action: "view", count: 3000 }]} />
    );
    expect(container.textContent).toContain("User Engagement");
    expect(container.textContent).toContain("150");
    expect(container.textContent).toContain("500");
    expect(container.textContent).toContain("30%");
    expect(container.textContent).toContain("view");
    expect(container.textContent).toContain("3,000");
  });
});
