import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ExportDataDialog } from "@/components/export-data-dialog";

describe("ExportDataDialog", () => {
  const sections = [
    { section: "settings", label: "Settings", included: true, estimatedSizeKb: 5 },
    { section: "analytics", label: "Analytics", included: true, estimatedSizeKb: 500 },
  ];
  it("renders export dialog", () => {
    const { container } = render(
      <ExportDataDialog appName="SuperApp" sections={sections} estimatedSizeDisplay="505KB"
        onExport={vi.fn()} onCancel={vi.fn()} />
    );
    expect(container.textContent).toContain("Export SuperApp Data");
    expect(container.textContent).toContain("Settings");
    expect(container.textContent).toContain("505KB");
    expect(container.textContent).toContain("Export JSON");
  });
});
