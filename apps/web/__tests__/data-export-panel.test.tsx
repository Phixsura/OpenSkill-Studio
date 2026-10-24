import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DataExportPanel } from "@/components/data-export-panel";
describe("DataExportPanel", () => {
  it("renders", () => {
    const { container } = render(
      <DataExportPanel total={2}
        exports={[
          { id: "exp-1", format: "csv", status: "completed", rowCount: 10000, sizeBytes: 5242880 },
          { id: "exp-2", format: "json", status: "failed", rowCount: 0, sizeBytes: 0 },
        ]} />
    );
    expect(container.textContent).toContain("Data Exports");
    expect(container.textContent).toContain("2 exports");
    expect(container.textContent).toContain("exp-1");
    expect(container.textContent).toContain("csv");
    expect(container.textContent).toContain("10,000 rows");
    expect(container.textContent).toContain("failed");
  });
});
