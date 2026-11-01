import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DataTable } from "@/components/data-table";

describe("DataTable", () => {
  it("renders table", () => {
    const onNext = vi.fn();
    const { container, getByText } = render(
      <DataTable columns={["name", "value"]}
        rows={[{ name: "A", value: 1 }, { name: "B", value: 2 }]}
        showing="1-2 of 50" hasNext={true} hasPrev={false}
        onNext={onNext} onPrev={vi.fn()} />
    );
    expect(container.textContent).toContain("name");
    expect(container.textContent).toContain("A");
    expect(container.textContent).toContain("B");
    expect(container.textContent).toContain("1-2 of 50");
    fireEvent.click(getByText("Next →"));
    expect(onNext).toHaveBeenCalled();
  });
});
