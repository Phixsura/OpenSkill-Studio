import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DataExportPanel } from "@/components/data-export-panel";

describe("DataExportPanel", () => {
  it("renders resources and formats", () => {
    const { container } = render(<DataExportPanel />);
    expect(container.textContent).toContain("extensions");
    expect(container.textContent).toContain("JSON");
  });
  it("triggers export", () => {
    const fn = vi.fn();
    const { container } = render(<DataExportPanel onExport={fn} />);
    const exportBtn = Array.from(container.querySelectorAll("button")).find(b => b.textContent?.includes("Export"));
    if (exportBtn) fireEvent.click(exportBtn);
    expect(fn).toHaveBeenCalledWith("extensions", "json");
  });
});
