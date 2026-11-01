import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ExportImportDialog } from "@/components/export-import-dialog";

describe("ExportImportDialog", () => {
  it("export mode", () => {
    const fn = vi.fn();
    const { container } = render(
      <ExportImportDialog mode="export" sections={["manifest", "settings"]}
        onExport={fn} onImport={vi.fn()} onClose={vi.fn()} />
    );
    expect(container.textContent).toContain("Export Config");
    expect(container.textContent).toContain("manifest");
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Export Selected")!);
    expect(fn).toHaveBeenCalled();
  });
  it("import mode", () => {
    const { container } = render(
      <ExportImportDialog mode="import" sections={[]}
        onExport={vi.fn()} onImport={vi.fn()} onClose={vi.fn()} />
    );
    expect(container.textContent).toContain("Import Config");
    expect(container.querySelector("textarea")).toBeTruthy();
  });
});
