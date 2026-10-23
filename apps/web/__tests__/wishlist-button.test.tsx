import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { WishlistButton } from "@/components/wishlist-button";

describe("WishlistButton", () => {
  it("not wishlisted", () => {
    const { container } = render(<WishlistButton isWishlisted={false} onToggle={vi.fn()} />);
    expect(container.textContent).toContain("Add to Wishlist");
    expect(container.textContent).toContain("🤍");
  });
  it("wishlisted", () => {
    const { container } = render(<WishlistButton isWishlisted={true} onToggle={vi.fn()} count={42} />);
    expect(container.textContent).toContain("Wishlisted");
    expect(container.textContent).toContain("❤️");
    expect(container.textContent).toContain("(42)");
  });
  it("toggles", () => {
    const fn = vi.fn();
    const { container } = render(<WishlistButton isWishlisted={false} onToggle={fn} />);
    fireEvent.click(container.querySelector("button")!);
    expect(fn).toHaveBeenCalled();
  });
});
