import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { WishlistButton } from "@/components/wishlist-button";

describe("WishlistButton", () => {
  it("renders not wishlisted", () => {
    const onToggle = vi.fn();
    const { container, getByText } = render(
      <WishlistButton wishlisted={false} count={42} onToggle={onToggle} />
    );
    expect(container.textContent).toContain("Add to Wishlist");
    expect(container.textContent).toContain("(42)");
    fireEvent.click(getByText(/Add to Wishlist/));
    expect(onToggle).toHaveBeenCalled();
  });

  it("renders wishlisted", () => {
    const { container } = render(
      <WishlistButton wishlisted={true} count={43} onToggle={vi.fn()} />
    );
    expect(container.textContent).toContain("Wishlisted");
  });
});
