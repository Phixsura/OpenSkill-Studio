import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MetricSummaryDashboard } from "@/components/metric-summary-dashboard";

describe("MetricSummaryDashboard", () => {
  const kpis = [
    { label: "Installs", value: 5000, display: "5,000", icon: "📥" },
    { label: "Rating", value: 4.8, display: "4.8/5", icon: "⭐" },
    { label: "Error Rate", value: 0.05, display: "0.05%", icon: "❌" },
  ];
  it("renders dashboard", () => {
    const { container } = render(
      <MetricSummaryDashboard appName="SuperApp" period="30d" kpis={kpis} healthScore={92} healthGrade="A" />
    );
    expect(container.textContent).toContain("SuperApp");
    expect(container.textContent).toContain("A");
    expect(container.textContent).toContain("92/100");
    expect(container.textContent).toContain("5,000");
    expect(container.textContent).toContain("4.8/5");
  });
});
