import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DataTable } from "@/components/data-table";

describe("DataTable", () => {
  const columns = [{ key: "name", label: "Name", sortable: true }];
  const rows = [{ name: "App A" }, { name: "App B" }];
  it("renders table", () => {
    const { container } = render(
      <DataTable columns={columns} rows={rows} total={2} page={1} totalPages={1}
        sortBy={null} sortDir="asc" onSort={vi.fn()} onPageChange={vi.fn()} />
    );
    expect(container.textContent).toContain("Name");
    expect(container.textContent).toContain("App A");
    expect(container.textContent).toContain("App B");
    expect(container.textContent).toContain("2 items");
  });
});
