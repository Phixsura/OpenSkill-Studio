import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { PaginationControls } from "@/components/pagination-controls";

describe("PaginationControls", () => {
  it("renders pages", () => {
    const { container } = render(<PaginationControls page={2} totalPages={5} onPageChange={vi.fn()} />);
    expect(container.textContent).toContain("1");
    expect(container.textContent).toContain("5");
  });
  it("navigates", () => {
    const fn = vi.fn();
    const { container } = render(<PaginationControls page={2} totalPages={5} onPageChange={fn} />);
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "→")!);
    expect(fn).toHaveBeenCalledWith(3);
  });
  it("hidden when 1 page", () => {
    const { container } = render(<PaginationControls page={1} totalPages={1} onPageChange={vi.fn()} />);
    expect(container.innerHTML).toBe("");
  });
});
