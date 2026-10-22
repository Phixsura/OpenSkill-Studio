import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DataExportPanel } from "@/components/data-export-panel";

describe("DataExportPanel", () => {
  it("renders form", () => {
    const { container } = render(<DataExportPanel onExport={vi.fn()} />);
    expect(container.textContent).toContain("Export Data");
    expect(container.querySelector("select")).toBeTruthy();
  });
  it("calls onExport", () => {
    const fn = vi.fn();
    const { container } = render(<DataExportPanel onExport={fn} />);
    const btn = container.querySelector("button")!;
    fireEvent.click(btn);
    expect(fn).toHaveBeenCalledWith("full", "json");
  });
  it("shows loading", () => {
    const { container } = render(<DataExportPanel onExport={vi.fn()} isExporting />);
    expect(container.textContent).toContain("Exporting...");
  });
});
