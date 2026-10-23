import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DataExportPage } from "@/components/data-export-page";

describe("DataExportPage", () => {
  it("renders and exports", () => {
    const onExport = vi.fn();
    const { container, getByText } = render(
      <DataExportPage onExport={onExport}
        types={[
          { type: "users", description: "All users", supports: ["json", "csv"] },
          { type: "apps", description: "All apps", supports: ["json"] },
        ]}
        lastExport={{ dataType: "users", format: "json", sizeDisplay: "12.5 KB", recordCount: 100 }} />
    );
    expect(container.textContent).toContain("Data Export");
    expect(container.textContent).toContain("Exported 100 users");
    expect(container.textContent).toContain("12.5 KB");
    fireEvent.click(getByText("Export"));
    expect(onExport).toHaveBeenCalled();
  });
});
