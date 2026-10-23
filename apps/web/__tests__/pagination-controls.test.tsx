import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { PaginationControls } from "@/components/pagination-controls";

describe("PaginationControls", () => {
  it("renders pagination", () => {
    const onPage = vi.fn();
    const { container, getByText } = render(
      <PaginationControls page={3} totalPages={10} pages={[1, 2, 3, 4, 5]}
        showing="21-30 of 100" hasPrev={true} hasNext={true} onPage={onPage} />
    );
    expect(container.textContent).toContain("21-30 of 100");
    expect(container.textContent).toContain("3");
    fireEvent.click(getByText("→"));
    expect(onPage).toHaveBeenCalledWith(4);
    fireEvent.click(getByText("1"));
    expect(onPage).toHaveBeenCalledWith(1);
  });
});
