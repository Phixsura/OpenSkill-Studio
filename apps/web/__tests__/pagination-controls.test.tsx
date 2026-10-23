import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { PaginationControls } from "@/components/pagination-controls";

describe("PaginationControls", () => {
  it("renders page buttons", () => {
    const { container } = render(
      <PaginationControls page={3} totalPages={10} hasPrev={true} hasNext={true} onPageChange={vi.fn()} />
    );
    expect(container.textContent).toContain("3");
    expect(container.textContent).toContain("←");
    expect(container.textContent).toContain("→");
  });
  it("calls onPageChange", () => {
    const fn = vi.fn();
    const { container } = render(
      <PaginationControls page={1} totalPages={5} hasPrev={false} hasNext={true} onPageChange={fn} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "→")!);
    expect(fn).toHaveBeenCalledWith(2);
  });
});
