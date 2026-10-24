import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SortableTable } from "@/components/sortable-table";

describe("SortableTable", () => {
  const columns = [
    { key: "name", label: "Name", sortable: true },
    { key: "downloads", label: "Downloads", sortable: true },
  ];
  const rows = [{ name: "Zapp", downloads: 100 }, { name: "Alpha", downloads: 500 }];

  it("renders rows", () => {
    const { container } = render(<SortableTable columns={columns} rows={rows} />);
    expect(container.textContent).toContain("Zapp");
    expect(container.textContent).toContain("Alpha");
    expect(container.querySelectorAll("tbody tr").length).toBe(2);
  });
  it("sorts on click", () => {
    const { container } = render(<SortableTable columns={columns} rows={rows} />);
    const btn = container.querySelector("button")!;
    fireEvent.click(btn);
    const cells = container.querySelectorAll("tbody tr td:first-child");
    expect(cells[0].textContent).toBe("Alpha");
  });
});
