import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { MetricsExportDialog } from "@/components/metrics-export-dialog";

describe("MetricsExportDialog", () => {
  const options = [{ id: "json", label: "JSON", icon: "📄" }, { id: "csv", label: "CSV", icon: "📊" }];
  it("renders", () => {
    const { container } = render(<MetricsExportDialog options={options} onExport={vi.fn()} onCancel={vi.fn()} />);
    expect(container.textContent).toContain("Export Metrics");
    expect(container.textContent).toContain("JSON");
    expect(container.textContent).toContain("CSV");
  });
  it("exports", () => {
    const fn = vi.fn();
    const { container } = render(<MetricsExportDialog options={options} onExport={fn} onCancel={vi.fn()} />);
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Export")!);
    expect(fn).toHaveBeenCalledWith("json");
  });
});
