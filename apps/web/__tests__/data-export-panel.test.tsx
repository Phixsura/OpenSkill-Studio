import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DataExportPanel } from "@/components/data-export-panel";

describe("DataExportPanel", () => {
  it("renders exports", () => {
    const { container } = render(
      <DataExportPanel totalSizeMb={7.5} onNewExport={vi.fn()} exports={[
        { id: "a1", name: "Users", format: "csv", rowCount: 5000, sizeMb: 5.0, status: "completed" },
        { id: "b2", name: "Orders", format: "json", rowCount: 2000, sizeMb: 2.5, status: "completed" },
      ]} />
    );
    expect(container.textContent).toContain("Data Exports");
    expect(container.textContent).toContain("2 exports");
    expect(container.textContent).toContain("Users");
    expect(container.textContent).toContain("csv");
    expect(container.textContent).toContain("5,000 rows");
    expect(container.textContent).toContain("json");
  });
});
