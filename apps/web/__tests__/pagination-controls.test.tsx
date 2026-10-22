import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { PaginationControls } from "@/components/pagination-controls";

describe("PaginationControls", () => {
  it("shows page info", () => {
    const { container } = render(<PaginationControls page={2} totalPages={5} onPageChange={vi.fn()} />);
    expect(container.textContent).toContain("Page 2 of 5");
  });

  it("hides for single page", () => {
    const { container } = render(<PaginationControls page={1} totalPages={1} onPageChange={vi.fn()} />);
    expect(container.innerHTML).toBe("");
  });

  it("calls onPageChange next", () => {
    const onChange = vi.fn();
    const { container } = render(<PaginationControls page={1} totalPages={3} onPageChange={onChange} />);
    fireEvent.click(container.querySelectorAll("button")[1]);
    expect(onChange).toHaveBeenCalledWith(2);
  });

  it("disables prev on first page", () => {
    const { container } = render(<PaginationControls page={1} totalPages={3} onPageChange={vi.fn()} />);
    expect(container.querySelectorAll("button")[0].disabled).toBe(true);
  });
});
