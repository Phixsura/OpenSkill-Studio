import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { PaginationInfoBar } from "@/components/pagination-info-bar";

describe("PaginationInfoBar", () => {
  it("renders", () => {
    const { container } = render(
      <PaginationInfoBar display="21-30 of 50" page={3} totalPages={5}
        pages={[1, 2, 3, 4, 5]} hasPrev={true} hasNext={true} onPageChange={vi.fn()} />
    );
    expect(container.textContent).toContain("21-30 of 50");
    expect(container.textContent).toContain("3");
    expect(container.textContent).toContain("←");
    expect(container.textContent).toContain("→");
  });
  it("next page", () => {
    const fn = vi.fn();
    const { container } = render(
      <PaginationInfoBar display="1-10" page={1} totalPages={3}
        pages={[1, 2, 3]} hasPrev={false} hasNext={true} onPageChange={fn} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "→")!);
    expect(fn).toHaveBeenCalledWith(2);
  });
});
