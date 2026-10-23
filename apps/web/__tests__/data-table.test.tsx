import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DataTable } from "@/components/data-table";

describe("DataTable", () => {
  const columns = [{ key: "name", label: "Name" }, { key: "installs", label: "Installs" }];
  const rows = [{ name: "App A", installs: 500 }, { name: "App B", installs: 1000 }];
  it("renders", () => {
    const { container } = render(
      <DataTable columns={columns} rows={rows} totalRows={2} page={1} totalPages={1}
        sortBy={null} sortDir="asc" onSort={vi.fn()} onPage={vi.fn()} />
    );
    expect(container.textContent).toContain("Name");
    expect(container.textContent).toContain("Installs");
    expect(container.textContent).toContain("App A");
    expect(container.textContent).toContain("1000");
    expect(container.textContent).toContain("2 rows");
  });
});
