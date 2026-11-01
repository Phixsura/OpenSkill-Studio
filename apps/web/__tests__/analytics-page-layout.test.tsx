import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AnalyticsPageLayout } from "@/components/analytics-page-layout";

describe("AnalyticsPageLayout", () => {
  const panels = [{ key: "installs", title: "Installs", icon: "📥" }, { key: "api", title: "API", icon: "🌐" }];
  it("renders", () => {
    const { container } = render(
      <AnalyticsPageLayout appName="MyApp" panels={panels} timeRanges={["7d", "30d"]}
        exportFormats={["csv"]} onTimeRangeChange={vi.fn()} onExport={vi.fn()}>
        <p>Chart here</p>
      </AnalyticsPageLayout>
    );
    expect(container.textContent).toContain("MyApp Analytics");
    expect(container.textContent).toContain("Installs");
    expect(container.textContent).toContain("7d");
    expect(container.textContent).toContain("Chart here");
  });
  it("time range change", () => {
    const fn = vi.fn();
    const { container } = render(
      <AnalyticsPageLayout appName="X" panels={panels} timeRanges={["7d", "90d"]}
        exportFormats={[]} onTimeRangeChange={fn} onExport={vi.fn()}>
        <p>C</p>
      </AnalyticsPageLayout>
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "7d")!);
    expect(fn).toHaveBeenCalledWith("7d");
  });
});
