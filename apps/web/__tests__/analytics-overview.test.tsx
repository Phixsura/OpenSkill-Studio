import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AnalyticsOverview } from "@/components/analytics-overview";

describe("AnalyticsOverview", () => {
  const metrics = [
    { label: "Installs", value: 1000, icon: "📥" },
    { label: "Rating", value: 4.5, icon: "⭐", display: "4.5/5" },
    { label: "Retention", value: 60, icon: "🔄", display: "60%" },
  ];
  it("renders analytics", () => {
    const { container } = render(
      <AnalyticsOverview metrics={metrics} period="30d" health="good" netInstalls={900} />
    );
    expect(container.textContent).toContain("Analytics Overview");
    expect(container.textContent).toContain("1,000");
    expect(container.textContent).toContain("4.5/5");
    expect(container.textContent).toContain("+900");
  });
});
