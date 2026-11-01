import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AnalyticsExportButton } from "@/components/analytics-export-button";

describe("AnalyticsExportButton", () => {
  it("renders button", () => {
    const { container } = render(
      <AnalyticsExportButton formats={["json", "csv"]} rowCount={100} onExport={vi.fn()} />
    );
    expect(container.textContent).toContain("Export (100 rows)");
  });
  it("opens dropdown", () => {
    const { container } = render(
      <AnalyticsExportButton formats={["json", "csv"]} rowCount={50} onExport={vi.fn()} />
    );
    fireEvent.click(container.querySelector("button")!);
    expect(container.textContent).toContain("json");
    expect(container.textContent).toContain("csv");
  });
});
