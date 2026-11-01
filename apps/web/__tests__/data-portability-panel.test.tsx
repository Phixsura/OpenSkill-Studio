import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DataPortabilityPanel } from "@/components/data-portability-panel";

const mockExports = [
  { id: "e1", dataTypes: ["settings", "users"], format: "json" as const, recordCount: 150, createdAt: "2024-01-01" },
];
const mockImports = [
  { id: "i1", status: "completed" as const, totalRecords: 50, imported: 45, skipped: 5, errors: [] },
];

describe("DataPortabilityPanel", () => {
  it("renders export tab", () => {
    const { container } = render(
      <DataPortabilityPanel exports={mockExports} imports={mockImports}
        availableTypes={["settings", "users", "content"]} />
    );
    expect(container.textContent).toContain("Data Portability");
    expect(container.textContent).toContain("settings");
    expect(container.textContent).toContain("150 records");
  });

  it("selects data types for export", () => {
    const onExport = vi.fn();
    const { getByText } = render(
      <DataPortabilityPanel exports={[]} imports={[]}
        availableTypes={["settings", "users"]} onExport={onExport} />
    );
    fireEvent.click(getByText("settings"));
    fireEvent.click(getByText("Export 1 type"));
    expect(onExport).toHaveBeenCalledWith(["settings"], "json");
  });

  it("switches to import tab", () => {
    const { getByText, container } = render(
      <DataPortabilityPanel exports={mockExports} imports={mockImports}
        availableTypes={[]} />
    );
    fireEvent.click(getByText("Import"));
    expect(container.textContent).toContain("45/50 imported");
    expect(container.textContent).toContain("5 skipped");
  });
});
