import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AppCardCompact } from "@/components/app-card-compact";

describe("AppCardCompact", () => {
  it("renders", () => {
    const { container } = render(
      <AppCardCompact id="a1" name="Auth SDK" developer="Alice" iconLetter="A"
        rating={4.7} starsDisplay="★★★★★" installDisplay="5K+"
        priceLabel="Free" category="security" onClick={vi.fn()} />
    );
    expect(container.textContent).toContain("Auth SDK");
    expect(container.textContent).toContain("Alice");
    expect(container.textContent).toContain("★★★★★");
    expect(container.textContent).toContain("5K+");
    expect(container.textContent).toContain("Free");
    expect(container.textContent).toContain("security");
  });
  it("click", () => {
    const fn = vi.fn();
    const { container } = render(
      <AppCardCompact id="a1" name="X" developer="Y" iconLetter="X" rating={4}
        starsDisplay="★★★★" installDisplay="100" priceLabel="$9.99"
        category="" onClick={fn} />
    );
    fireEvent.click(container.querySelector("button")!);
    expect(fn).toHaveBeenCalledWith("a1");
  });
});
