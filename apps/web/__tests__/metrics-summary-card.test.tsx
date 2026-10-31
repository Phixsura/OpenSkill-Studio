import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MetricsSummaryCard } from "@/components/metrics-summary-card";

describe("MetricsSummaryCard", () => {
  it("renders metrics", () => {
    const metrics = [
      { label: "Installs", value: 1234, trend: "up" as const, changePct: 12 },
      { label: "Errors", value: "0.5%", trend: "down" as const, changePct: -30 },
    ];
    const { container } = render(<MetricsSummaryCard title="Overview" metrics={metrics} />);
    expect(container.textContent).toContain("1,234");
    expect(container.textContent).toContain("Installs");
    expect(container.textContent).toContain("12%");
  });
  it("shows flat trend", () => {
    const { container } = render(
      <MetricsSummaryCard title="T" metrics={[{ label: "X", value: 0, trend: "flat" }]} />
    );
    expect(container.textContent).toContain("→");
  });
});
