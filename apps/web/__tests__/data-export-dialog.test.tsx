import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DataExportDialog } from "@/components/data-export-dialog";

describe("DataExportDialog", () => {
  it("renders and exports", () => {
    const onExport = vi.fn();
    const { container, getByText } = render(
      <DataExportDialog availableFormats={["csv", "json"]} rowCount={1500} onExport={onExport} />
    );
    expect(container.textContent).toContain("Export Data");
    expect(container.textContent).toContain("1,500");
    fireEvent.click(getByText("json"));
    fireEvent.click(getByText("Export as JSON"));
    expect(onExport).toHaveBeenCalledWith("json");
  });
});
