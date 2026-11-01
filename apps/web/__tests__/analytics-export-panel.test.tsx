import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AnalyticsExportPanel } from "@/components/analytics-export-panel";

const reports = [{ reportId: "rpt-1", extensionId: "ext-1", period: "daily", metrics: { total_events: 50, by_event: { install: 30 } }, generatedAt: Date.now() }];

describe("AnalyticsExportPanel", () => {
  it("renders reports", () => {
    const { container } = render(<AnalyticsExportPanel reports={reports} />);
    expect(container.textContent).toContain("rpt-1");
    expect(container.textContent).toContain("50 events");
  });
  it("generate report", () => {
    const fn = vi.fn();
    const { container } = render(<AnalyticsExportPanel reports={[]} onGenerate={fn} />);
    const genBtn = Array.from(container.querySelectorAll("button")).find(b => b.textContent?.includes("Generate"));
    if (genBtn) fireEvent.click(genBtn);
    expect(fn).toHaveBeenCalledWith("daily");
  });
});
