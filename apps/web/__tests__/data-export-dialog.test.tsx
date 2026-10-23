import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DataExportDialog } from "@/components/data-export-dialog";

describe("DataExportDialog", () => {
  const formats = [
    { id: "csv", label: "CSV", icon: "📊", description: "Spreadsheet" },
    { id: "json", label: "JSON", icon: "📋", description: "Developer" },
  ];
  it("renders", () => {
    const { container } = render(
      <DataExportDialog formats={formats} rowCount={250} onExport={vi.fn()} onClose={vi.fn()} />
    );
    expect(container.textContent).toContain("Export Data");
    expect(container.textContent).toContain("250");
    expect(container.textContent).toContain("CSV");
    expect(container.textContent).toContain("JSON");
  });
  it("exports selected", () => {
    const fn = vi.fn();
    const { container } = render(
      <DataExportDialog formats={formats} rowCount={10} onExport={fn} onClose={vi.fn()} />
    );
    const exportBtn = Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Export")!;
    fireEvent.click(exportBtn);
    expect(fn).toHaveBeenCalledWith("csv");
  });
});
