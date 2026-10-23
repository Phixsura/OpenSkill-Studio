import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { PaginationControls } from "@/components/pagination-controls";

describe("PaginationControls", () => {
  const meta = { page: 2, per_page: 10, total: 50, total_pages: 5, has_next: true, has_prev: true };
  it("renders", () => {
    const { container } = render(<PaginationControls meta={meta} onPageChange={vi.fn()} />);
    expect(container.textContent).toContain("11–20 of 50");
    expect(container.textContent).toContain("2");
  });
  it("next page", () => {
    const fn = vi.fn();
    const { container } = render(<PaginationControls meta={meta} onPageChange={fn} />);
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "→")!);
    expect(fn).toHaveBeenCalledWith(3);
  });
});
