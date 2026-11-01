import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AnalyticsExportBtn } from "@/components/analytics-export-btn";

describe("AnalyticsExportBtn", () => {
  it("renders and exports", () => {
    const onExport = vi.fn();
    const { container, getByText } = render(
      <AnalyticsExportBtn formats={["json", "csv"]} period="30d"
        onExport={onExport} lastExport={{ format: "json", sizeDisplay: "12.5 KB" }} />
    );
    expect(container.textContent).toContain("Export 30d");
    expect(container.textContent).toContain("12.5 KB");
    fireEvent.click(getByText(/Export/));
    expect(onExport).toHaveBeenCalledWith("json");
  });
});
