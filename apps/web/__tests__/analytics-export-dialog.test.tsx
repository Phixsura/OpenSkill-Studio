import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AnalyticsExportDialog } from "@/components/analytics-export-dialog";

describe("AnalyticsExportDialog", () => {
  it("renders", () => {
    const { container } = render(<AnalyticsExportDialog onExport={vi.fn()} onClose={vi.fn()} />);
    expect(container.textContent).toContain("Export Analytics");
    expect(container.textContent).toContain("JSON");
    expect(container.textContent).toContain("CSV");
    expect(container.textContent).toContain("Markdown");
  });
  it("export", () => {
    const fn = vi.fn();
    const { container } = render(<AnalyticsExportDialog onExport={fn} onClose={vi.fn()} />);
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent?.includes("Export as"))!);
    expect(fn).toHaveBeenCalledWith("json");
  });
});
